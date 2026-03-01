# config.py — רשימת נכסים מורחבת ל-2026

# מניות הליבה שלך (יופיעו תמיד בתיק האישי)
MY_STOCKS_BASE = [
    "MSFT", "AAPL", "NVDA", "TSLA", "PLTR",
    "ENLT.TA", "POLI.TA", "LUMI.TA"
]

# רשימת הסריקה המלאה: ת"א, עולם, סחורות וקריפטו
SCAN_LIST = [
    # --- מניות ארה"ב חזקות ומומנטום ---
    "AMZN", "AVGO", "META", "GOOGL", "LLY", "TSM", "COST", "V", "ADBE", "NFLX", "AMD",
    "MU", "SMCI", "GEV", "NEE", "CRDO", "CRVS", "GEHC", 

    # --- בורסת תל אביב (TASE) ---
    "ICL.TA", "TSEM.TA", "BEZQ.TA", "NICE.TA", "AZRG.TA", "DSCT.TA", 
    "ESLT.TA", "NXSN.TA", 

    # --- מניות עולם (אירופה ואסיה) ---
    "ASML", "NVO", "MC.PA", "SAP", "RHM.DE", "SONY",

    # --- סחורות ואנרגיה (זהב, כסף, נפט, דלק, נחושת) ---
    "GC=F",     # זהב (Gold)
    "SI=F",     # כסף (Silver)
    "CL=F",     # נפט גולמי (Crude Oil)
    "HO=F",     # דלק/סולר (Heating Oil)
    "HG=F",     # נחושת (Copper)
    "BZ=F",     # נפט ברנט (Brent)

    # --- קריפטו ---
    "BTC-USD", "ETH-USD", "SOL-USD", "XRP-USD", "DOGE-USD"
]

HELP = {
    "symbol": "סימול הנכס בבורסה.",
    "score": "ציון AI (0-6) המעיד על איכות החברה.",
    "action": "המלצת פעולה בזמן אמת.",
    "rev_growth": "צמיחה במכירות מעל 10%?",
}

HEBREW_SUMMARIES = {
    "ESLT.TA": "אלביט מערכות — מובילה ביטחונית ישראלית.",
    "NXSN.TA": "נקסט ויז'ן — צמיחה אגרסיבית בפתרונות צילום.",
    "GC=F":    "זהב — הגנה אינפלציונית ומקלט בטוח.",
    "CL=F":    "נפט גולמי — מדד האנרגיה העולמי.",
}
