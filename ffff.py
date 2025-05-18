{
  "$setWindowFields": {
    "partitionBy": {
      "productRic": "$_id.productRic",
      "counterpartyType": "$_id.counterpartyType"
    },
    "sortBy": {"_id.timeBin": 1},
    "output": {
      "cumulativeTrades": {
        "$sum": "$tradeCount",
        "window": {"documents": ["unbounded", "current"]}
      }
    }
  }
}
