#!/usr/bin/env python3
import json
import os
from dotenv import load_dotenv
load_dotenv()
from modeling.dcf import *  
from modeling.data import *


# use the same assumptions you wire into the front-end:
ASSUMPTIONS = {
    "forecast": 5,
    "discount_rate": 0.10,
    "earnings_growth_rate": 0,  # EG for AAPL
    "cap_ex_growth_rate": 0.045,
    "perpetual_growth_rate": 0.02,
    "interval": "annual",
    "apikey": os.environ["FMP_API_KEY"]   # FMP key
}

out = {}
for ticker, eg in [("AAPL",0.062),("MSFT",0.19),("META",0.173)]:
    args = ASSUMPTIONS.copy()
    args["earnings_growth_rate"] = eg
    dcfs = historical_DCF(
      ticker,
      years  = args["forecast"],
      forecast           = args["forecast"],
      discount_rate      = args["discount_rate"],
      earnings_growth_rate = args["earnings_growth_rate"],
      cap_ex_growth_rate   = args["cap_ex_growth_rate"],
      perpetual_growth_rate= args["perpetual_growth_rate"],
      interval           = args["interval"],
      apikey             = args["apikey"],
    )
    # pick the most recent year (year=0) result
    latest_date = max(dcfs)
    res = dcfs[latest_date]
    out[ticker] = {
      "enterpriseValue": res["enterprise_value"],
      "equityValue":     res["equity_value"],
      "sharePrice":      res["share_price"],
      "projections":     [ { "year": p["year"], 
                             "freeCashFlow": p["freeCashFlow"], 
                             "discountedCashFlow": p["discountedCashFlow"] } 
                           for p in res["projections"] ]
    }

with open("frontend/src/data/dcf_static.json","w") as f:
    json.dump(out, f, indent=2)
print("Exported dcf_static.json")
