# Local sector/theme mapping for the scanner's "Industry Cluster" grouping.
#
# WHY THIS EXISTS: the original code tried to pull this from "https://githubusercontent.com",
# which isn't a real file URL (it's a bare domain), so it always failed. There's no reliable,
# free, always-live JSON feed for "which index a stock belongs to", so this is kept as a local
# static reference instead - it only affects the sector *label* shown in the UI.
#
# This does NOT affect correctness of prices, security IDs, or F&O lot sizes - those are always
# pulled live from Dhan's instrument master in main.py. Only the grouping label comes from here.
#
# NSE reshuffles index constituents quarterly - review/update this list periodically.

SECTOR_MAP = {
    # Nifty Bank
    "HDFCBANK": "Nifty Bank", "ICICIBANK": "Nifty Bank", "SBIN": "Nifty Bank",
    "KOTAKBANK": "Nifty Bank", "AXISBANK": "Nifty Bank", "INDUSINDBK": "Nifty Bank",
    "BANKBARODA": "Nifty Bank", "PNB": "Nifty Bank", "IDFCFIRSTB": "Nifty Bank", "AUBANK": "Nifty Bank",

    # Nifty IT
    "TCS": "Nifty IT", "INFY": "Nifty IT", "HCLTECH": "Nifty IT", "WIPRO": "Nifty IT",
    "TECHM": "Nifty IT", "LTIM": "Nifty IT", "PERSISTENT": "Nifty IT",
    "COFORGE": "Nifty IT", "MPHASIS": "Nifty IT",

    # Nifty Auto
    "MARUTI": "Nifty Auto", "TATAMOTORS": "Nifty Auto", "M&M": "Nifty Auto",
    "BAJAJ-AUTO": "Nifty Auto", "HEROMOTOCO": "Nifty Auto", "EICHERMOT": "Nifty Auto",
    "TVSMOTOR": "Nifty Auto", "ASHOKLEY": "Nifty Auto", "BHARATFORG": "Nifty Auto",

    # Nifty Pharma
    "SUNPHARMA": "Nifty Pharma", "DRREDDY": "Nifty Pharma", "CIPLA": "Nifty Pharma",
    "DIVISLAB": "Nifty Pharma", "LUPIN": "Nifty Pharma", "AUROPHARMA": "Nifty Pharma",
    "TORNTPHARM": "Nifty Pharma", "ZYDUSLIFE": "Nifty Pharma", "ALKEM": "Nifty Pharma",

    # Nifty FMCG
    "HINDUNILVR": "Nifty FMCG", "ITC": "Nifty FMCG", "NESTLEIND": "Nifty FMCG",
    "BRITANNIA": "Nifty FMCG", "TATACONSUM": "Nifty FMCG", "DABUR": "Nifty FMCG",
    "GODREJCP": "Nifty FMCG", "MARICO": "Nifty FMCG", "COLPAL": "Nifty FMCG",

    # Nifty Metal
    "TATASTEEL": "Nifty Metal", "JSWSTEEL": "Nifty Metal", "HINDALCO": "Nifty Metal",
    "VEDL": "Nifty Metal", "JINDALSTEL": "Nifty Metal", "SAIL": "Nifty Metal",
    "NMDC": "Nifty Metal", "HINDZINC": "Nifty Metal", "NATIONALUM": "Nifty Metal",

    # Nifty Energy
    "RELIANCE": "Nifty Energy", "ONGC": "Nifty Energy", "NTPC": "Nifty Energy",
    "POWERGRID": "Nifty Energy", "COALINDIA": "Nifty Energy", "BPCL": "Nifty Energy",
    "IOC": "Nifty Energy", "GAIL": "Nifty Energy", "TATAPOWER": "Nifty Energy",

    # Nifty Realty
    "DLF": "Nifty Realty", "GODREJPROP": "Nifty Realty", "OBEROIRLTY": "Nifty Realty",
    "PHOENIXLTD": "Nifty Realty", "PRESTIGE": "Nifty Realty", "LODHA": "Nifty Realty",
}
