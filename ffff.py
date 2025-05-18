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
          // Step 1: Get current counterparty type
          "currentCounterparty": "$$this.counterpartyType",
          
          // Step 2: Update cumulative trades for this counterparty
          "updatedCumulative": {
            "$mergeObjects": [
              "$$value.cumulativeTrades",
              {
                "$arrayToObject": [
                  [
                    {
                      "k": "$$this.counterpartyType",
                      "v": {
                        "$add": [
                          {"$ifNull": [{"$getField": {"field": "$$this.counterpartyType", "input": "$$value.cumulativeTrades"}}, 0]},
                          "$$this.current.trades"
                        ]
                      }
                    }
                  ]
                ]
              }
            ]
          },
          
          // Step 3: Build the output document
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
                            {"$ifNull": [{"$getField": {"field": "$$this.counterpartyType", "input": "$$value.cumulativeTrades"}}, 0]},
                            "$$this.current.trades"
                          ]
                        }
                      }
                    }
                  ]
                }
              ]
            ]
          },
          
          // Step 4: Return updated state
          "cumulativeTrades": "$$updatedCumulative",
          "processedSeries": "$$processedSeries"
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
