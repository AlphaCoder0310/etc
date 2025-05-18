{
  "$addFields": {
    "timeSeries": {
      "$reduce": {
        "input": "$timeSeries",
        "initialValue": {
          "cumulativeByCounterparty": {}, // Stores running totals per counterpartyType
          "processedSeries": [] // Final output with cumulative data
        },
        "in": {
          // Update cumulative totals for each counterparty
          "cumulativeByCounterparty": {
            "$mergeObjects": [
              "$$value.cumulativeByCounterparty",
              {
                "$arrayToObject": {
                  "$map": {
                    "input": ["$$this"], // Process each time entry
                    "as": "entry",
                    "in": {
                      "k": "$$entry.counterpartyType",
                      "v": {
                        "trades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$entry.counterpartyType.trades", 0]}, 0]},
                            "$$entry.current.trades"
                          ]
                        },
                        "totalQuantity": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$entry.counterpartyType.totalQuantity", 0]}, 0]},
                            "$$entry.current.totalQuantity"
                          ]
                        },
                        "buyTrades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$entry.counterpartyType.buyTrades", 0]}, 0]},
                            "$$entry.current.buyTrades"
                          ]
                        },
                        "sellTrades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$entry.counterpartyType.sellTrades", 0]}, 0]},
                            "$$entry.current.sellTrades"
                          ]
                        },
                        "buyVolume": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$entry.counterpartyType.buyVolume", 0]}, 0]},
                            "$$entry.current.buyVolume"
                          ]
                        },
                        "sellVolume": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$entry.counterpartyType.sellVolume", 0]}, 0]},
                            "$$entry.current.sellVolume"
                          ]
                        }
                      }
                    }
                  }
                }
              }
            ]
          },
          // Build the output with cumulative data
          "processedSeries": {
            "$concatArrays": [
              "$$value.processedSeries",
              [
                {
                  "$mergeObjects": [
                    "$$this",
                    {
                      "cumulative": {
                        "trades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$this.counterpartyType.trades", 0]}, 0]},
                            "$$this.current.trades"
                          ]
                        },
                        "totalQuantity": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$this.counterpartyType.totalQuantity", 0]}, 0]},
                            "$$this.current.totalQuantity"
                          ]
                        },
                        "buyTrades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$this.counterpartyType.buyTrades", 0]}, 0]},
                            "$$this.current.buyTrades"
                          ]
                        },
                        "sellTrades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$this.counterpartyType.sellTrades", 0]}, 0]},
                            "$$this.current.sellTrades"
                          ]
                        },
                        "buyVolume": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$this.counterpartyType.buyVolume", 0]}, 0]},
                            "$$this.current.buyVolume"
                          ]
                        },
                        "sellVolume": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeByCounterparty.$$this.counterpartyType.sellVolume", 0]}, 0]},
                            "$$this.current.sellVolume"
                          ]
                        }
                      }
                    }
                  ]
                }
              ]
            ]
          }
        }
      }
    }
  }
},
{
  "$project": {
    "timeSeries": "$timeSeries.processedSeries",
    "_id": 0
  }
}
