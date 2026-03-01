# config.py — רשימת נכסים מורחבת ל-2026

# מניות הליבה שלך (יופיעו תמיד בתיק)
MY_STOCKS_BASE = ["MSFT", "AAPL", "NVDA", "TSLA", "PLTR", "ENLT.TA", "POLI.TA", "LUMI.TA"]

# רשימת הסריקה המלאה: ת"א, עולם, סחורות וקריפטו
SCAN_LIST = [
    # --- מניות ארה"ב חזקות ומומנטום ---
    "AMZN", "AVGO", "META", "GOOGL", "LLY", "TSM", "COST", "V", "ADBE", "NFLX", "AMD",
    "MU", "SMCI", "GEV", "NEE", "CRDO", "CRVS", "GEHC", 

    # --- בורסת תל אביב (TASE) ---
    "ICL.TA", "TSEM.TA", "BEZQ.TA", "NICE.TA", "AZRG.TA", "DSCT.TA", 
    "ESLT.TA", "NXSN.TA", 

    # --- מניות עולם ---
    "ASML", "NVO", "MC.PA", "SAP", "RHM.DE",

    # --- סחורות ואנרגיה (דלק, נפט, זהב, כסף, נחושת) ---
    "GC=F", "SI=F", "CL=F", "HO=F", "BZ=F", "HG=F",

    # --- קריפטו ---
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD"
]

HEBREW_SUMMARIES = {
    "ESLT.TA": "אלביט מערכות — מובילה ביטחונית.",
    "NXSN.TA": "נקסט ויז'ן — צמיחה אדירה בצילום רחפנים.",
    "GC=F":    "זהב — הגנה אינפלציונית.",
    "CL=F":    "נפט גולמי — מדד האנרגיה העולמי.",
}
