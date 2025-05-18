{
  "$addFields": {
    "timeSeries": {
      "$reduce": {
        "input": "$timeSeries",
        "initialValue": {
          "cumulativeTrades": {}, // Stores running trade counts per counterparty
          "processedSeries": []   // Final output with cumulative data
        },
        "in": {
          // Update cumulative trades for this counterparty
          "cumulativeTrades": {
            "$mergeObjects": [
              "$$value.cumulativeTrades",
              {
                "$$this.counterpartyType": {
                  "$add": [
                    {"$ifNull": ["$$value.cumulativeTrades.$$this.counterpartyType", 0]},
                    "$$this.current.trades"
                  ]
                }
              }
            ]
          },
          // Build the output with cumulative trades
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
                            {"$ifNull": ["$$value.cumulativeTrades.$$this.counterpartyType", 0]},
                            "$$this.current.trades"
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
