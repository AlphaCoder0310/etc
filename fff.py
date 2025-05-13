# 1. Time Handling with Validation
    try:
        target_date = datetime(1970, 1, 1) + timedelta(days=epoch_day)
        start_datetime = (datetime.combine(target_date, start_time) 
                         if start_time else None)
        end_datetime = (datetime.combine(target_date, end_time) 
                       if end_time else None)
        
        # Validate time range
        if start_datetime and end_datetime and start_datetime > end_datetime:
            raise ValueError("Start time cannot be after end time")
            
    except Exception as e:
        raise ValueError(f"Invalid time parameters: {str(e)}")

    # 2. Base Query Construction
    match_stage = {
        "metadata.epochDay": epoch_day,
        "timestamp": {"$exists": True}  # Ensure timestamp exists
    }
    
    # 3. Product Filter with Validation
    if product_ric:
        if isinstance(product_ric, str):
            match_stage["metadata.productRic"] = product_ric
        elif isinstance(product_ric, (list, tuple)):
            if not product_ric:
                raise ValueError("Product RIC list cannot be empty")
            match_stage["metadata.productRic"] = {"$in": list(product_ric)}
        else:
            raise TypeError("product_ric must be string or list")

    # 4. Time Filter with Edge Cases
    if start_datetime or end_datetime:
        time_filter = {}
        if start_datetime:
            time_filter["$gte"] = start_datetime
        if end_datetime:
            time_filter["$lte"] = end_datetime
        match_stage["timestamp"] = time_filter

    if order_id:
        match_stage["metadata.orderId"] = str(order_id)

    # 5. Counterparty Processing
    if counterparty_mapping:
        if not isinstance(counterparty_mapping, dict):
            raise TypeError("counterparty_mapping must be a dictionary")
            
        mapping_expr = {
            '$switch': {
                'branches': [
                    {'case': {'$eq': ['$$cp', k]}, 'then': v}
                    for k, v in counterparty_mapping.items()
                ],
                'default': 'other'
            }
        }
        unique_counterparty_types = list(set(counterparty_mapping.values()))
    else:
        mapping_expr = {'$literal': 'unknown'}
        unique_counterparty_types = []

    # 6. Get Product RICs with Caching
    if product_ric is None:
        product_rics = collection.distinct(
            "metadata.productRic", 
            match_stage,
            maxTimeMS=5000  # 5 second timeout
        )
        if not product_rics:
            raise ValueError("No products found for the given filters")
    else:
        product_rics = [product_ric] if isinstance(product_ric, str) else product_ric

    pipeline = [
        {'$match': match_stage},
        
        # Add 1-second time bins
        {
            '$addFields': {
                'timeBin': {
                    '$dateTrunc': {
                        'date': '$timestamp',
                        'unit': 'second',
                        'binSize': 1
                    }
                }
            }
        },
        
        # First grouping by product, counterparty, side, and time bin
        {
            '$group': {
                '_id': {
                    'productRic': '$metadata.productRic',
                    'counterparty': '$lastExecutedCounterparty',
                    'side': '$side',
                    'timeBin': '$timeBin'
                },
                'tradeCount': {'$sum': 1},
                'totalQuantity': {'$sum': '$lastExecutedQuantity'},
                'firstPrice': {'$first': '$lastExecutedPrice'},
                'firstTimestamp': {'$min': '$timestamp'},
                'lastTimestamp': {'$max': '$timestamp'}
            }
        },
        
        # Add counterparty type classification
        {
            '$addFields': {
                'counterpartyType': {
                    '$let': {
                        'vars': {'cp': {'$toLower': {'$trim': {'input': '$_id.counterparty'}}}},
                        'in': mapping_expr
                    }
                }
            }
        },
        
        # Dual facet approach for parallel processing
        {
            '$facet': {
                **{
                    f"product_{product}": [
                        {'$match': {'_id.productRic': product}},
                        
                        # Sort chronologically before calculating running totals
                        {'$sort': {'_id.timeBin': 1}},
                        
                        # Calculate global totals and running sums
                        {
                            '$group': {
                                '_id': None,
                                'globalTotalTrades': {'$sum': '$tradeCount'},
                                'globalTotalVolume': {'$sum': '$totalQuantity'},
                                'timeSeries': {
                                    '$push': {
                                        'timeBin': '$_id.timeBin',
                                        'counterpartyType': '$counterpartyType',
                                        'side': '$_id.side',
                                        'currentTrades': '$tradeCount',
                                        'currentQuantity': '$totalQuantity',
                                        'firstPrice': '$firstPrice'
                                    }
                                },
                                'docs': {'$push': '$$ROOT'}
                            }
                        },
                        
                        # Unwind to add running totals
                        {'$unwind': {'path': '$docs', 'includeArrayIndex': 'idx'}},
                        
                        # Calculate cumulative metrics
                        {
                            '$addFields': {
                                'docs.cumulativeTrades': {
                                    '$sum': {
                                        '$slice': [
                                            '$timeSeries.currentTrades',
                                            {'$add': ['$idx', 1]}
                                        ]
                                    }
                                },
                                'docs.cumulativeQuantity': {
                                    '$sum': {
                                        '$slice': [
                                            '$timeSeries.currentQuantity',
                                            {'$add': ['$idx', 1]}
                                        ]
                                    }
                                }
                            }
                        },
                        
                        # Re-group by counterparty type
                        {
                            '$group': {
                                '_id': '$docs.counterpartyType',
                                'productRic': {'$first': '$docs._id.productRic'},
                                'globalTotalTrades': {'$first': '$globalTotalTrades'},
                                'globalTotalVolume': {'$first': '$globalTotalVolume'},
                                'timeSeries': {
                                    '$push': {
                                        'timeBin': '$docs._id.timeBin',
                                        'current': {
                                            'side': '$docs._id.side',
                                            'trades': '$docs.tradeCount',
                                            'quantity': '$docs.totalQuantity',
                                            'price': '$docs.firstPrice'
                                        },
                                        'cumulative': {
                                            'trades': '$docs.cumulativeTrades',
                                            'quantity': '$docs.cumulativeQuantity'
                                        }
                                    }
                                },
                                'counterparties': {
                                    '$push': {
                                        'name': '$docs._id.counterparty',
                                        'tradeCount': '$docs.tradeCount',
                                        'totalQuantity': '$docs.totalQuantity'
                                    }
                                }
                            }
                        }
                    ]
                    for product in product_rics
                }
            }
        },
        
        # Final output restructuring
        {
            '$project': {
                'allProducts': {
                    '$map': {
                        'input': {'$objectToArray': '$$ROOT'},
                        'as': 'product',
                        'in': {
                            'productRic': {'$substrBytes': ['$$product.k', 8, -1]},  # Remove "product_" prefix
                            'counterparties': '$$product.v'
                        }
                    }
                }
            }
        },
        {'$unwind': '$allProducts'},
        {'$replaceRoot': {'newRoot': '$allProducts'}}
    ]

#version mongodb5.0
pipeline = [
    {'$match': match_stage},
    
    # 1. Bin by 1-second intervals and add counterparty type in a single stage
    {
        '$addFields': {
            'timeBin': {'$dateTrunc': {'date': '$timestamp', 'unit': 'second'}},
            'counterpartyType': {
                '$let': {
                    'vars': {'cp': {'$toLower': {'$trim': {'input': '$lastExecutedCounterparty'}}}},
                    'in': mapping_expr
                }
            }
        }
    },
    
    # 2. Group by all dimensions in a single pass
    {
        '$group': {
            '_id': {
                'productRic': '$metadata.productRic',
                'counterpartyType': '$counterpartyType',
                'timeBin': '$timeBin',
                'side': '$side'
            },
            'tradeCount': {'$sum': 1},
            'totalQuantity': {'$sum': '$lastExecutedQuantity'},
            'firstPrice': {'$first': '$lastExecutedPrice'},
            'firstTimestamp': {'$min': '$timestamp'},
            'lastTimestamp': {'$max': '$timestamp'}
        }
    },
    
    # 3. Sort chronologically before window calculations
    {'$sort': {'_id.productRic': 1, '_id.counterpartyType': 1, '_id.timeBin': 1}},
    
    # 4. Calculate running totals using window functions (MongoDB 5.0+)
    {
        '$setWindowFields': {
            'partitionBy': {
                'productRic': '$_id.productRic',
                'counterpartyType': '$_id.counterpartyType'
            },
            'sortBy': {'_id.timeBin': 1},
            'output': {
                'cumulativeTrades': {
                    '$sum': '$tradeCount',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                },
                'cumulativeQuantity': {
                    '$sum': '$totalQuantity',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                }
            }
        }
    },
    
    # 5. Final grouping to structure output
    pipeline = [
    {'$match': match_stage},
    
    # 1. Bin by 1-second intervals and add counterparty type in a single stage
    {
        '$addFields': {
            'timeBin': {'$dateTrunc': {'date': '$timestamp', 'unit': 'second'}},
            'counterpartyType': {
                '$let': {
                    'vars': {'cp': {'$toLower': {'$trim': {'input': '$lastExecutedCounterparty'}}}},
                    'in': mapping_expr
                }
            }
        }
    },
    
    # 2. Group by all dimensions in a single pass
    {
        '$group': {
            '_id': {
                'productRic': '$metadata.productRic',
                'counterpartyType': '$counterpartyType',
                'timeBin': '$timeBin',
                'side': '$side'
            },
            'tradeCount': {'$sum': 1},
            'totalQuantity': {'$sum': '$lastExecutedQuantity'},
            'firstPrice': {'$first': '$lastExecutedPrice'},
            'firstTimestamp': {'$min': '$timestamp'},
            'lastTimestamp': {'$max': '$timestamp'}
        }
    },
    
    # 3. Sort chronologically before window calculations
    {'$sort': {'_id.productRic': 1, '_id.counterpartyType': 1, '_id.timeBin': 1}},
    
    # 4. Calculate running totals using window functions (MongoDB 5.0+)
    {
        '$setWindowFields': {
            'partitionBy': {
                'productRic': '$_id.productRic',
                'counterpartyType': '$_id.counterpartyType'
            },
            'sortBy': {'_id.timeBin': 1},
            'output': {
                'cumulativeTrades': {
                    '$sum': '$tradeCount',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                },
                'cumulativeQuantity': {
                    '$sum': '$totalQuantity',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                }
            }
        }
    },
    
    # 5. Final grouping to structure output
   pipeline = [
    {'$match': match_stage},
    
    # 1. Bin by 1-second intervals and add counterparty type in a single stage
    {
        '$addFields': {
            'timeBin': {'$dateTrunc': {'date': '$timestamp', 'unit': 'second'}},
            'counterpartyType': {
                '$let': {
                    'vars': {'cp': {'$toLower': {'$trim': {'input': '$lastExecutedCounterparty'}}}},
                    'in': mapping_expr
                }
            }
        }
    },
    
    # 2. Group by all dimensions in a single pass
    {
        '$group': {
            '_id': {
                'productRic': '$metadata.productRic',
                'counterpartyType': '$counterpartyType',
                'timeBin': '$timeBin',
                'side': '$side'
            },
            'tradeCount': {'$sum': 1},
            'totalQuantity': {'$sum': '$lastExecutedQuantity'},
            'firstPrice': {'$first': '$lastExecutedPrice'},
            'firstTimestamp': {'$min': '$timestamp'},
            'lastTimestamp': {'$max': '$timestamp'}
        }
    },
    
    # 3. Sort chronologically before window calculations
    {'$sort': {'_id.productRic': 1, '_id.counterpartyType': 1, '_id.timeBin': 1}},
    
    # 4. Calculate running totals using window functions (MongoDB 5.0+)
    {
        '$setWindowFields': {
            'partitionBy': {
                'productRic': '$_id.productRic',
                'counterpartyType': '$_id.counterpartyType'
            },
            'sortBy': {'_id.timeBin': 1},
            'output': {
                'cumulativeTrades': {
                    '$sum': '$tradeCount',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                },
                'cumulativeQuantity': {
                    '$sum': '$totalQuantity',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                }
            }
        }
    },
    
# 5. Final grouping to structure output
pipeline = [
    {'$match': match_stage},
    
    # 1. Bin by 1-second intervals and add counterparty type in a single stage
    {
        '$addFields': {
            'timeBin': {'$dateTrunc': {'date': '$timestamp', 'unit': 'second'}},
            'counterpartyType': {
                '$let': {
                    'vars': {'cp': {'$toLower': {'$trim': {'input': '$lastExecutedCounterparty'}}}},
                    'in': mapping_expr
                }
            }
        }
    },
    
    # 2. Group by all dimensions in a single pass
    {
        '$group': {
            '_id': {
                'productRic': '$metadata.productRic',
                'counterpartyType': '$counterpartyType',
                'timeBin': '$timeBin',
                'side': '$side'
            },
            'tradeCount': {'$sum': 1},
            'totalQuantity': {'$sum': '$lastExecutedQuantity'},
            'firstPrice': {'$first': '$lastExecutedPrice'},
            'firstTimestamp': {'$min': '$timestamp'},
            'lastTimestamp': {'$max': '$timestamp'}
        }
    },
    
    # 3. Sort chronologically before window calculations
    {'$sort': {'_id.productRic': 1, '_id.counterpartyType': 1, '_id.timeBin': 1}},
    
    # 4. Calculate running totals using window functions (MongoDB 5.0+)
    {
        '$setWindowFields': {
            'partitionBy': {
                'productRic': '$_id.productRic',
                'counterpartyType': '$_id.counterpartyType'
            },
            'sortBy': {'_id.timeBin': 1},
            'output': {
                'cumulativeTrades': {
                    '$sum': '$tradeCount',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                },
                'cumulativeQuantity': {
                    '$sum': '$totalQuantity',
                    'window': {
                        'documents': ['unbounded', 'current']
                    }
                }
            }
        }
    },
    
    # 5. Final grouping to structure output
    {
        '$group': {
            '_id': {
                'productRic': '$_id.productRic',
                'counterpartyType': '$_id.counterpartyType'
            },
            'timeSeries': {
                '$push': {
                    'timeBin': '$_id.timeBin',
                    'current': {
                        'side': '$_id.side',
                        'trades': '$tradeCount',
                        'quantity': '$totalQuantity',
                        'price': '$firstPrice'
                    },
                    'cumulative': {
                        'trades': '$cumulativeTrades',
                        'quantity': '$cumulativeQuantity'
                    }
                }
            },
            'counterparties': {
                '$push': {
                    'name': '$_id.counterparty',
                    'tradeCount': '$tradeCount',
                    'totalQuantity': '$totalQuantity'
                }
            },
            'globalTotalTrades': {'$sum': '$tradeCount'},
            'globalTotalVolume': {'$sum': '$totalQuantity'}
        }
    },
    
    # 6. Project to final format
    {
        '$project': {
            'productRic': '$_id.productRic',
            'counterpartyType': '$_id.counterpartyType',
            'timeSeries': 1,
            'counterparties': 1,
            'globalMetrics': {
                'totalTrades': '$globalTotalTrades',
                'totalVolume': '$globalTotalVolume'
            },
            '_id': 0
        }
    }
]

{
    "productRic": "AAPL.O",
    "counterparties": [
        {
            "_id": "latencyarb",
            "timeSeries": [
                {
                    "timeBin": ISODate("2023-06-01T09:30:00Z"),
                    "current": {
                        "side": "buy",
                        "trades": 3,
                        "quantity": 450,
                        "price": 125.25
                    },
                    "cumulative": {
                        "trades": 3,
                        "quantity": 450
                    }
                },
                {
                    "timeBin": ISODate("2023-06-01T09:30:01Z"),
                    "current": {
                        "side": "sell",
                        "trades": 2,
                        "quantity": 300,
                        "price": 125.30
                    },
                    "cumulative": {
                        "trades": 5,
                        "quantity": 750
                    }
                }
            ],
            "counterparties": [
                {
                    "name": "CP1",
                    "tradeCount": 5,
                    "totalQuantity": 750
                }
            ]
        }
    ]
}