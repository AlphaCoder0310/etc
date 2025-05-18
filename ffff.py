{
  "$addFields": {
    "timeSeries": {
      "$reduce": {
        "input": "$timeSeries",
        "initialValue": {
          "cumulativeTrades": {},  $ Will store {counterpartyType1: total1, counterpartyType2: total2}
          "processedSeries": []    $ Final output with cumulative data
        },
        "in": {
          $ Step 1: Store current counterparty type in a variable
          "currentCpType": "$$this.counterpartyType",
          
          $ Step 2: Calculate the new cumulative total
          "newTotal": {
            "$add": [
              {"$ifNull": [
                {"$getField": {
                  "field": {"$literal": "$$this.counterpartyType"},
                  "input": "$$value.cumulativeTrades"
                }},
                0
              ]},
              "$$this.current.trades"
            ]
          },
          
          $ Step 3: Update cumulative trades object
          "updatedCumulative": {
            "$mergeObjects": [
              "$$value.cumulativeTrades",
              {
                "$arrayToObject": [
                  [
                    {
                      "k": {"$literal": "$$this.counterpartyType"},
                      "v": "$$newTotal"
                    }
                  ]
                ]
              }
            ]
          },
          
          $ Step 4: Build the output document
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
          
          $ Step 5: Return updated state
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
