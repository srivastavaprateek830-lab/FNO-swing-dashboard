import pandas as pd

def get_master_market_feed() -> pd.DataFrame:
    """MASTER THEMATIC DICTIONARY: Houses the full live NSE F&O universe mapping."""
    raw_market_map = {
        "Nifty Bank": [
            {"Symbol": "HDFCBANK", "ID": "1333", "Sector": "Nifty Bank", "FnO": True, "LotSize": 550},
            {"Symbol": "ICICIBANK", "ID": "11483", "Sector": "Nifty Bank", "FnO": True, "LotSize": 700},
            {"Symbol": "SBIN", "ID": "3045", "Sector": "Nifty Bank", "FnO": True, "LotSize": 1500},
            {"Symbol": "AXISBANK", "ID": "5900", "Sector": "Nifty Bank", "FnO": True, "LotSize": 625},
            {"Symbol": "KOTAKBANK", "ID": "1922", "Sector": "Nifty Bank", "FnO": True, "LotSize": 400},
            {"Symbol": "INDUSINDBK", "ID": "5258", "Sector": "Nifty Bank", "FnO": True, "LotSize": 450},
            {"Symbol": "BANKBARODA", "ID": "4668", "Sector": "Nifty Bank", "FnO": True, "LotSize": 1250},
            {"Symbol": "PNB", "ID": "10666", "Sector": "Nifty Bank", "FnO": True, "LotSize": 4000},
            {"Symbol": "CANBK", "ID": "10794", "Sector": "Nifty Bank", "FnO": True, "LotSize": 2250},
            {"Symbol": "FEDERALBNK", "ID": "10242", "Sector": "Nifty Bank", "FnO": True, "LotSize": 5000}
        ],
        "Nifty Auto": [
            {"Symbol": "TATAMOTORS", "ID": "3456", "Sector": "Nifty Auto", "FnO": True, "LotSize": 1425},
            {"Symbol": "MARUTI", "ID": "10999", "Sector": "Nifty Auto", "FnO": True, "LotSize": 50},
            {"Symbol": "M&M", "ID": "2031", "Sector": "Nifty Auto", "FnO": True, "LotSize": 350},
            {"Symbol": "BAJAJ-AUTO", "ID": "16669", "Sector": "Nifty Auto", "FnO": True, "LotSize": 125},
            {"Symbol": "HEROMOTOCO", "ID": "1348", "Sector": "Nifty Auto", "FnO": True, "LotSize": 300},
            {"Symbol": "EICHERMOT", "ID": "910", "Sector": "Nifty Auto", "FnO": True, "LotSize": 175},
            {"Symbol": "TVSMOTOR", "ID": "8442", "Sector": "Nifty Auto", "FnO": True, "LotSize": 350},
            {"Symbol": "ASHOKLEY", "ID": "212", "Sector": "Nifty Auto", "FnO": True, "LotSize": 2500}
        ],
        "Nifty IT": [
            {"Symbol": "TCS", "ID": "11536", "Sector": "Nifty IT", "FnO": True, "LotSize": 175},
            {"Symbol": "INFY", "ID": "1594", "Sector": "Nifty IT", "FnO": True, "LotSize": 400},
            {"Symbol": "HCLTECH", "ID": "1345", "Sector": "Nifty IT", "FnO": True, "LotSize": 350},
            {"Symbol": "LTIM", "ID": "17832", "Sector": "Nifty IT", "FnO": True, "LotSize": 150},
            {"Symbol": "WIPRO", "ID": "3787", "Sector": "Nifty IT", "FnO": True, "LotSize": 1500},
            {"Symbol": "TECHM", "ID": "13357", "Sector": "Nifty IT", "FnO": True, "LotSize": 600},
            {"Symbol": "COFORGE", "ID": "11543", "Sector": "Nifty IT", "FnO": True, "LotSize": 150},
            {"Symbol": "PERSISTENT", "ID": "18365", "Sector": "Nifty IT", "FnO": True, "LotSize": 200}
        ],
        "Nifty Pharma": [
            {"Symbol": "SUNPHARMA", "ID": "3333", "Sector": "Nifty Pharma", "FnO": True, "LotSize": 350},
            {"Symbol": "CIPLA", "ID": "694", "Sector": "Nifty Pharma", "FnO": True, "LotSize": 650},
            {"Symbol": "DRREDDY", "ID": "881", "Sector": "Nifty Pharma", "FnO": True, "LotSize": 125},
            {"Symbol": "LUPIN", "ID": "1994", "Sector": "Nifty Pharma", "FnO": True, "LotSize": 400},
            {"Symbol": "DIVISLAB", "ID": "10940", "Sector": "Nifty Pharma", "FnO": True, "LotSize": 200},
            {"Symbol": "AUROPHARMA", "ID": "275", "Sector": "Nifty Pharma", "FnO": True, "LotSize": 550}
        ],
        "Nifty FMCG": [
            {"Symbol": "HINDUNILVR", "ID": "1330", "Sector": "Nifty FMCG", "FnO": True, "LotSize": 300},
            {"Symbol": "ITC", "ID": "1660", "Sector": "Nifty FMCG", "FnO": True, "LotSize": 1600},
            {"Symbol": "BRITANNIA", "ID": "547", "Sector": "Nifty FMCG", "FnO": True, "LotSize": 200},
            {"Symbol": "NESTLEIND", "ID": "17963", "Sector": "Nifty FMCG", "FnO": True, "LotSize": 400},
            {"Symbol": "TATACONSUM", "ID": "3432", "Sector": "Nifty FMCG", "FnO": True, "LotSize": 600},
            {"Symbol": "DABUR", "ID": "772", "Sector": "Nifty FMCG", "FnO": True, "LotSize": 1250}
        ],
        "Nifty Metal": [
            {"Symbol": "TATASTEEL", "ID": "3499", "Sector": "Nifty Metal", "FnO": True, "LotSize": 5500},
            {"Symbol": "JSWSTEEL", "ID": "11723", "Sector": "Nifty Metal", "FnO": True, "LotSize": 675},
            {"Symbol": "HINDALCO", "ID": "1363", "Sector": "Nifty Metal", "FnO": True, "LotSize": 1400},
            {"Symbol": "VEDL", "ID": "3521", "Sector": "Nifty Metal", "FnO": True, "LotSize": 2300},
            {"Symbol": "JINDALSTEL", "ID": "11725", "Sector": "Nifty Metal", "FnO": True, "LotSize": 625}
        ],
        "Nifty Oil & Gas": [
            {"Symbol": "RELIANCE", "ID": "2885", "Sector": "Nifty Oil & Gas", "FnO": True, "LotSize": 250},
            {"Symbol": "ONGC", "ID": "2475", "Sector": "Nifty Oil & Gas", "FnO": True, "LotSize": 3850},
            {"Symbol": "BPCL", "ID": "526", "Sector": "Nifty Oil & Gas", "FnO": True, "LotSize": 1800},
            {"Symbol": "IOC", "ID": "1624", "Sector": "Nifty Oil & Gas", "FnO": True, "LotSize": 3250},
            {"Symbol": "GAIL", "ID": "4717", "Sector": "Nifty Oil & Gas", "FnO": True, "LotSize": 4550}
        ],
        "Nifty Power & Infra": [
            {"Symbol": "NTPC", "ID": "11630", "Sector": "Nifty Power & Infra", "FnO": True, "LotSize": 1500},
            {"Symbol": "POWERGRID", "ID": "14977", "Sector": "Nifty Power & Infra", "FnO": True, "LotSize": 3600},
            {"Symbol": "LT", "ID": "11485", "Sector": "Nifty Power & Infra", "FnO": True, "LotSize": 300},
            {"Symbol": "ADANIPORTS", "ID": "15083", "Sector": "Nifty Power & Infra", "FnO": True, "LotSize": 400}
        ],
        "Nifty Commodities": [
            {"Symbol": "ACC", "ID": "22", "Sector": "Nifty Commodities", "FnO": True, "LotSize": 300},
            {"Symbol": "AMBUJACEM", "ID": "63", "Sector": "Nifty Commodities", "FnO": True, "LotSize": 1500},
            {"Symbol": "GRASIM", "ID": "1233", "Sector": "Nifty Commodities", "FnO": True, "LotSize": 400},
            {"Symbol": "ULTRACEMCO", "ID": "11523", "Sector": "Nifty Commodities", "FnO": True, "LotSize": 100}
        ],
        "Nifty Services": [
            {"Symbol": "DLF", "ID": "14732", "Sector": "Nifty Services", "FnO": True, "LotSize": 825},
            {"Symbol": "GODREJPROP", "ID": "17823", "Sector": "Nifty Services", "FnO": True, "LotSize": 325},
            {"Symbol": "INDIGO", "ID": "20123", "Sector": "Nifty Services", "FnO": True, "LotSize": 300}
        ]
    }
    compiled_list = []
    for sector_name, stocks in raw_market_map.items():
        for s in stocks:
            compiled_list.append(s)
    return pd.DataFrame(compiled_list)
