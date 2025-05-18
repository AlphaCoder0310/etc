{
  "$addFields": {
    "counterpartySeries": {
      "$reduce": {
        "input": "$timeSeries",
        "initialValue": {
          "cumulativeData": {},
          "processed": []
        },
        "in": {
          "cumulativeData": {
            "$mergeObjects": [
              "$$value.cumulativeData",
              {
                "$arrayToObject": {
                  "$map": {
                    "input": "$$this.counterparties",
                    "as": "cp",
                    "in": {
                      "k": "$$cp.counterpartyType",
                      "v": {
                        "trades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.trades", 0]}, 0]},
                            "$$cp.current.trades"
                          ]
                        },
                        "totalQuantity": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.totalQuantity", 0]}, 0]},
                            "$$cp.current.totalQuantity"
                          ]
                        },
                        "buyTrades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.buyTrades", 0]}, 0]},
                            "$$cp.current.buyTrades"
                          ]
                        },
                        "sellTrades": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.sellTrades", 0]}, 0]},
                            "$$cp.current.sellTrades"
                          ]
                        },
                        "buyVolume": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.buyVolume", 0]}, 0]},
                            "$$cp.current.buyVolume"
                          ]
                        },
                        "sellVolume": {
                          "$add": [
                            {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.sellVolume", 0]}, 0]},
                            "$$cp.current.sellVolume"
                          ]
                        }
                      }
                    }
                  }
                }
              }
            ]
          },
          "processed": {
            "$concatArrays": [
              "$$value.processed",
              [
                {
                  "timeBin": "$$this.timeBin",
                  "counterparties": {
                    "$map": {
                      "input": "$$this.counterparties",
                      "as": "cp",
                      "in": {
                        "$mergeObjects": [
                          "$$cp",
                          {
                            "cumulative": {
                              "trades": {
                                "$add": [
                                  {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.trades", 0]}, 0]},
                                  "$$cp.current.trades"
                                ]
                              },
                              "totalQuantity": {
                                "$add": [
                                  {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.totalQuantity", 0]}, 0]},
                                  "$$cp.current.totalQuantity"
                                ]
                              },
                              "buyTrades": {
                                "$add": [
                                  {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.buyTrades", 0]}, 0]},
                                  "$$cp.current.buyTrades"
                                ]
                              },
                              "sellTrades": {
                                "$add": [
                                  {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.sellTrades", 0]}, 0]},
                                  "$$cp.current.sellTrades"
                                ]
                              },
                              "buyVolume": {
                                "$add": [
                                  {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.buyVolume", 0]}, 0]},
                                  "$$cp.current.buyVolume"
                                ]
                              },
                              "sellVolume": {
                                "$add": [
                                  {"$ifNull": [{"$arrayElemAt": ["$$value.cumulativeData.$$cp.counterpartyType.sellVolume", 0]}, 0]},
                                  "$$cp.current.sellVolume"
                                ]
                              }
                            }
                          }
                        ]
                      }
                    }
                  }
                }
              ]
            ]
          }
        }
      }
    }
  }
}
