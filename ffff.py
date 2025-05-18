  // Calculate running totals per counterparty
  {
    "$setWindowFields": {
      "partitionBy": {
        "counterpartyType": "$_id.counterpartyType"
      },
      "sortBy": { "_id.timeBin": 1 },
      "output": {
        "cumulativeTrades": {
          "$sum": "$current.trades",
          "window": { "documents": ["unbounded", "current"] }
        },
        "cumulativeQuantity": {
          "$sum": "$current.totalQuantity",
          "window": { "documents": ["unbounded", "current"] }
        },
        "cumulativeBuyTrades": {
          "$sum": "$current.buyTrades",
          "window": { "documents": ["unbounded", "current"] }
        },
        "cumulativeSellTrades": {
          "$sum": "$current.sellTrades",
          "window": { "documents": ["unbounded", "current"] }
        },
        "cumulativeBuyVolume": {
          "$sum": "$current.buyVolume",
          "window": { "documents": ["unbounded", "current"] }
        },
        "cumulativeSellVolume": {
          "$sum": "$current.sellVolume",
          "window": { "documents": ["unbounded", "current"] }
        }
      }
    }
  },
  
  // Final grouping with _id: null to create single document output
  {
    "$group": {
      "_id": null,
      "timeSeries": {
        "$push": {
          "timeBin": "$_id.timeBin",
          "counterpartyType": "$_id.counterpartyType",
          "side": "$_id.side",
          "current": "$current",
          "cumulative": {
            "trades": "$cumulativeTrades",
            "totalQuantity": "$cumulativeQuantity",
            "buyTrades": "$cumulativeBuyTrades",
            "sellTrades": "$cumulativeSellTrades",
            "buyVolume": "$cumulativeBuyVolume",
            "sellVolume": "$cumulativeSellVolume"
          }
        }
      }
    }
  },
  
  // Final projection
  {
    "$project": {
      "timeSeries": 1,
      "_id": 0
    }
  }
