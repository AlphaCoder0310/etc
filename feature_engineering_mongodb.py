from datetime import datetime, timedelta, time
import pandas as pd
from pymongo import MongoClient
from functools import lru_cache

@lru_cache(maxsize=1)
def load_broker_mapping(csv_path):
    """Optimized CSV loader with direct dict conversion"""
    return pd.read_csv(csv_path).set_index('code')['type'].to_dict()

def query_combined(collection, epoch_day, product_ric=None, start_time=None, end_time=None, 
                   counterparty_mapping=None, order_id=None, limit=None):
    """
    Optimized trading analytics query with dual-level faceting.
    Returns: {productRic: {counterpartyType: {metrics, counterparts}}}
    """
    # Time handling optimization
    target_date = datetime(1970, 1, 1) + timedelta(days=epoch_day)
    start_datetime = datetime.combine(target_date, start_time) if start_time else None
    end_datetime = datetime.combine(target_date, end_time) if end_time else None

    # Base query construction
    match_stage = {"metadata.epochDay": epoch_day}
    
    # Product filter - handles None/str/list cases
    if product_ric:
        match_stage["metadata.productRic"] = (
            product_ric if isinstance(product_ric, str) 
            else {"$in": product_ric}
        )

    # Time filter - only add if specified
    if start_datetime and end_datetime:
        match_stage["timestamp"] = {"$gte": start_datetime, "$lte": end_datetime}

    if order_id:
        match_stage["metadata.orderId"] = order_id

    # Counterparty processing
    if counterparty_mapping:
        mapping_expr = {
            '$switch': {
                'branches': [
                    {'case': {'$eq': ['$$cp', k]}, 'then': v}
                    for k, v in counterparty_mapping.items()
                ],
                'default': 'other'
            }
        }
        # Define unique types right before use
        unique_counterparty_types = list(set(counterparty_mapping.values()))
    else:
        mapping_expr = {'$literal': 'unknown'}
        unique_counterparty_types = []

    # Get product RICs if not specified - optimized distinct query
    product_rics = []
    if product_ric is None:
        product_rics = collection.distinct("metadata.productRic", match_stage)
    elif isinstance(product_ric, str):
        product_rics = [product_ric]
    else:
        product_rics = product_ric

    # Main aggregation pipeline
    pipeline = [
        {'$match': match_stage},
        # First grouping stage
        {
            '$group': {
                '_id': {
                    'productRic': '$metadata.productRic',
                    'counterparty': '$lastExecutedCounterparty',
                    'side': '$side'
                },
                'tradeCount': {'$sum': 1},
                'buyTradeCount': {'$sum': {'$cond': [{'$eq': ['$_id.side', 1]}, 1, 0]}},
                'sellTradeCount': {'$sum': {'$cond': [{'$eq': ['$_id.side', 2]}, 1, 0]}},
                'totalQuantity': {'$sum': '$lastExecutedQuantity'},
                'botSize': {'$first': '$botSize'},
                'soldSize': {'$first': '$soldSize'},
                'executedQuantity': {'$first': '$executedQuantity'},
                'counterpartyBotSize': {'$sum': {'$cond': [{'$eq': ['$_id.side', 1]}, '$lastExecutedQuantity', 0]}},
                'counterpartySoldSize': {'$sum': {'$cond': [{'$eq': ['$_id.side', 2]}, '$lastExecutedQuantity', 0]}},
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
                        # Calculate global totals first
                        {
                            '$group': {
                                '_id': None,
                                'globalTotalTrades': {'$sum': '$tradeCount'},
                                'globalTotalVolume': {'$sum': '$totalQuantity'},
                                'globalTimeRange': {
                                    '$push': {
                                        'first': '$firstTimestamp',
                                        'last': '$lastTimestamp'
                                    }
                                },
                                'docs': {'$push': '$$ROOT'}
                            }
                        },
                        {'$unwind': '$docs'},
                        {
                            '$replaceRoot': {
                                'newRoot': {
                                    '$mergeObjects': [
                                        '$docs',
                                        {
                                            'globalTotalTrades': '$globalTotalTrades',
                                            'globalTotalVolume': '$globalTotalVolume',
                                            'globalTimeRange': '$globalTimeRange'
                                        }
                                    ]
                                }
                            }
                        },
                        # Then group by counterparty type
                        {
                            '$group': {
                                '_id': '$counterpartyType',
                                'productRic': {'$first': '$_id.productRic'},
                                'globalTotalTrades': {'$first': '$globalTotalTrades'},
                                'globalTotalVolume': {'$first': '$globalTotalVolume'},
                                'globalTimeRange': {'$first': '$globalTimeRange'},
                                'totalTrades': {'$sum': '$tradeCount'},
                                'buyTrades': {'$sum': '$buyTradeCount'},
                                'sellTrades': {'$sum': '$sellTradeCount'},
                                'totalVolume': {'$sum': '$totalQuantity'},
                                'buyVolume': {'$sum': '$counterpartyBotSize'},
                                'sellVolume': {'$sum': '$counterpartySoldSize'},
                                'totalExecutedQuantity': {'$sum': '$counterpartyExecutedQuantity'},
                                'timeRange': {
                                    '$push': {
                                        'first': '$firstTimestamp',
                                        'last': '$lastTimestamp'
                                    }
                                },
                                'counterparties': {
                                    '$push': {
                                        'name': '$_id.counterparty',
                                        'tradeCount': '$tradeCount',
                                        'buyTradeCount': '$buyTradeCount',
                                        'sellTradeCount': '$sellTradeCount',
                                        'totalQuantity': '$totalQuantity',
                                        'side': {
                                            '$switch': {
                                                'branches': [
                                                    {'case': {'$gt': ['$buyTradeCount', '$sellTradeCount']}, 'then': 'PREDOMINANTLY_BUY'},
                                                    {'case': {'$gt': ['$sellTradeCount', '$buyTradeCount']}, 'then': 'PREDOMINANTLY_SELL'},
                                                    {'case': {'$eq': ['$buyTradeCount', '$sellTradeCount']}, 'then': 'BALANCED'}
                                                ]
                                            }
                                        }
                                    }
                                }
                            }
                        },
                        # Nested facet for counterparty types
                        {
                            '$facet': {
                                **{
                                    cp_type: [
                                        {'$match': {'$expr': {'$eq': [
                                            {'$toLower': {'$trim': {'input': '$_id'}}},
                                            {'$toLower': {'$trim': {'input': cp_type}}}
                                        ]}}},
                                        {
                                            '$addFields': {
                                                'metrics': {
                                                    'activity': {
                                                        'trades': {
                                                            'total': '$totalTrades',
                                                            'buy': '$buyTrades',
                                                            'sell': '$sellTrades',
                                                            'imbalance': {
                                                                '$divide': [
                                                                    {'$subtract': ['$buyTrades', '$sellTrades']},
                                                                    {'$max': ['$totalTrades', 1]}
                                                                ]
                                                            },
                                                            'frequency': {
                                                                '$divide': [
                                                                    '$totalTrades',
                                                                    {
                                                                        '$max': [
                                                                            {
                                                                                '$divide': [
                                                                                    {'$subtract': [
                                                                                        {'$max': '$globalTimeRange.last'},
                                                                                        {'$min': '$globalTimeRange.first'}
                                                                                    ]},
                                                                                    60000
                                                                                ]
                                                                            },
                                                                            0.01667
                                                                        ]
                                                                    }
                                                                ]
                                                            }
                                                        },
                                                        'volume': {
                                                            'total': '$totalVolume',
                                                            'buy': '$buyVolume',
                                                            'sell': '$sellVolume',
                                                            'imbalance': {
                                                                '$divide': [
                                                                    {'$subtract': ['$buyVolume', '$sellVolume']},
                                                                    {'$max': ['$totalVolume', 1]}
                                                                ]
                                                            },
                                                            'perTrade': {
                                                                '$divide': [
                                                                    '$totalVolume',
                                                                    {'$max': ['$totalTrades', 1]}
                                                                ]
                                                            }
                                                        }
                                                    },
                                                    'participation': {
                                                        'byTrades': {
                                                            '$divide': ['$totalTrades', '$globalTotalTrades']  # Use pre-calculated global
                                                        },
                                                        'byVolume': {
                                                            '$divide': ['$totalVolume', '$globalTotalVolume']
                                                        }
                                                    }
                                                }
                                            }
                                        },
                                        {
                                            '$project': {
                                                'productRic': 1,
                                                'metrics': {
                                                    'activity': {
                                                        'trades': {
                                                            'total': 1,
                                                            'buy': 1,
                                                            'sell': 1,
                                                            'imbalance': {'$round': ['$metrics.activity.trades.imbalance', 4]},
                                                            'frequency': {'$round': ['$metrics.activity.trades.frequency', 2]}
                                                        },
                                                        'volume': {
                                                            'total': 1,
                                                            'buy': 1,
                                                            'sell': 1,
                                                            'imbalance': {'$round': ['$metrics.activity.volume.imbalance', 4]},
                                                            'perTrade': {'$round': ['$metrics.activity.volume.perTrade', 0]}
                                                        }
                                                    },
                                                    'participation': {
                                                        'byTrades': {'$round': ['$metrics.participation.byTrades', 4]},
                                                        'byVolume': {'$round': ['$metrics.participation.byVolume', 4]}
                                                    }
                                                },
                                                'counterparties': 1
                                            }
                                        }
                                    ]
                                    for cp_type in unique_counterparty_types
                                }
                            }
                        }
                    ]
                    for product in product_rics
                }
            }
        },
        # Restructure the output
        {
            '$project': {
                'allProducts': {
                    '$map': {
                        'input': {'$objectToArray': '$$ROOT'},
                        'as': 'product',
                        'in': {
                            'productRic': {'$substrBytes': ['$$product.k', 8, -1]},
                            'counterparties': {
                                '$reduce': {
                                    'input': '$$product.v',
                                    'initialValue': {},
                                    'in': {
                                        '$mergeObjects': [
                                            '$$value',
                                            {
                                                '$$this._id': {
                                                    'metrics': '$$this.metrics',
                                                    'counterparties': '$$this.counterparties'
                                                }
                                            }
                                        ]
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        {'$unwind': '$allProducts'},
        {'$replaceRoot': {'newRoot': '$allProducts'}},
        {
            '$project': {
                'productRic': 1,
                'counterparties': {
                    '$arrayToObject': {
                        '$filter': {
                            'input': {
                                '$map': {
                                    'input': {'$objectToArray': '$counterparties'},
                                    'as': 'ct',
                                    'in': {
                                        'k': '$$ct.k',
                                        'v': {
                                            '$cond': [
                                                {
                                                    '$and': [
                                                        {'$ne': ['$$ct.v', None]},
                                                        {'$gt': [{'$size': {'$ifNull': ['$$ct.v.counterparties', []]}}, 0]}
                                                    ]
                                                },
                                                '$$ct.v',
                                                None
                                            ]
                                        }
                                    }
                                }
                            },
                            'as': 'ct',
                            'cond': {'$ne': ['$$ct.v', None]}
                        }
                    }
                },
                '_id': 0
            }
        }
    ]

    if limit:
        pipeline.append({'$limit': limit})

    # Execute with performance optimizations
    try:
        cursor = collection.aggregate(
            pipeline,
            allowDiskUse=True,
            maxTimeMS=30000,  # 30 second timeout
            batchSize=1000,   # Better memory handling
            comment='high_freq_trading_analytics'  # For query profiling
        )

        # Efficient result transformation
        output = {}
        for product in cursor:
            product_ric = product['productRic']
            output[product_ric] = {}
            
            for cp_type, data in product['counterparties'].items():
                output[product_ric][cp_type] = {
                    'metrics': data['metrics'],
                    'counterparties': data['counterparties']
                }
        
        return output

    except Exception as e:
        print(f"Aggregation pipeline error: {str(e)}")
        return {}
