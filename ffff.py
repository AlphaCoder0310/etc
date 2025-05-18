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
          // Step 1: Update cumulative trades for this counterparty
          "updatedCumulative": {
            "$let": {
              "vars": {
                "cpType": "$$this.counterpartyType",
                "currentTrades": "$$this.current.trades",
                "previousTotal": {
                  "$ifNull": [
                    {"$getField": {
                      "field": "$$this.counterpartyType",
                      "input": "$$value.cumulativeTrades"
                    }},
                    0
                  ]
                }
              },
              "in": {
                "$mergeObjects": [
                  "$$value.cumulativeTrades",
                  {"$arrayToObject": [[{
                    "k": "$$cpType",
                    "v": {"$add": ["$$previousTotal", "$$currentTrades"]}
                  }]]}
                ]
              }
            }
          },
          
          // Step 2: Build the output document
          "processedSeries": {
            "$let": {
              "vars": {
                "currentTotal": {
                  "$add": [
                    {"$ifNull": [
                      {"$getField": {
                        "field": "$$this.counterpartyType",
                        "input": "$$value.cumulativeTrades"
                      }},
                      0
                    ]},
                    "$$this.current.trades"
                  ]
                }
              },
              "in": {
                "$concatArrays": [
                  "$$value.processedSeries",
                  [{
                    "$mergeObjects": [
                      "$$this",
                      {"cumulative": {"trades": "$$currentTotal"}}
                    ]
                  }]
                ]
              }
            }
          },
          
          // Step 3: Return updated state
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
