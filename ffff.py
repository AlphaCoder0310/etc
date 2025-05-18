{
  "$addFields": {
    "timeSeries": {
      "$reduce": {
        "input": "$timeSeries",
        "initialValue": {
          "cumulativeTrades": {},  // Will store {counterpartyType1: total1, counterpartyType2: total2}
          "processedSeries": []    // Final output with cumulative data
        },
        "in": {
          "$let": {
            "vars": {
              "currentCpType": "$$this.counterpartyType",
              "currentTrades": "$$this.current.trades",
              "previousTotal": {
                "$ifNull": [
                  {"$getField": {
                    "field": {"$literal": "$$this.counterpartyType"},
                    "input": "$$value.cumulativeTrades"
                  }},
                  0
                ]
              },
              "newTotal": {
                "$add": ["$$previousTotal", "$$currentTrades"]
              }
            },
            "in": {
              "cumulativeTrades": {
                "$mergeObjects": [
                  "$$value.cumulativeTrades",
                  {
                    "$arrayToObject": [
                      [
                        {
                          "k": "$$currentCpType",
                          "v": "$$newTotal"
                        }
                      ]
                    ]
                  }
                ]
              },
              "processedSeries": {
                "$concatArrays": [
                  "$$value.processedSeries",
                  [
                    {
                      "$mergeObjects": [
                        "$$this",
                        {
                          "cumulative": {
                            "trades": "$$newTotal"
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
    }
  }
},
{
  "$project": {
    "timeSeries": "$timeSeries.processedSeries",
    "_id": 0
  }
}
