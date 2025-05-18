{
  "$addFields": {
    "timeSeries": {
      "$reduce": {
        "input": "$timeSeries",
        "initialValue": {
          "cumulativeTrades": {},  // Stores {counterpartyType: totalTrades}
          "processedSeries": []    // Final output with cumulative data
        },
        "in": {
          // Step 1: Get the current counterparty type from the timeSeries entry
          "currentCpType": "$$this.counterpartyType",
          
          // Step 2: Calculate new cumulative total
          "newTotal": {
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
          },
          
          // Step 3: Update cumulativeTrades object
          "updatedCumulative": {
            "$mergeObjects": [
              "$$value.cumulativeTrades",
              {"$arrayToObject": [[{
                "k": "$$this.counterpartyType",
                "v": "$$newTotal"
              }]]}
            ]
          },
          
          // Step 4: Build the output document
          "processedSeries": {
            "$concatArrays": [
              "$$value.processedSeries",
              [{
                "$mergeObjects": [
                  "$$this",
                  {
                    "cumulative": {
                      "trades": "$$newTotal"
                    }
                  }
                ]
              }]
            ]
          },
          
          // Step 5: Return the updated state
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
