import sqlite3
import pandas as pd
import datetime

DB_NAME = "hub_data.db"

def _get_conn():
    return sqlite3.connect(DB_NAME, check_same_thread=False)

def init_db():
    conn = _get_conn()
    cursor = conn.cursor()
    # טבלה לתיק הסוכנים: שומרת מחיר קנייה ומחיר נוכחי לחישוב P&L
    cursor.execute('''CREATE TABLE IF NOT EXISTS agent_portfolio 
                      (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                       symbol TEXT, buy_price REAL, current_price REAL, 
                       agent_type TEXT, timestamp TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def save_agent_trade(symbol, price, agent_type):
    conn = _get_conn()
    cursor = conn.cursor()
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO agent_portfolio (symbol, buy_price, current_price, agent_type, timestamp, status) VALUES (?,?,?,?,?,?)",
                   (symbol, price, price, agent_type, now, "OPEN"))
    conn.commit()
    conn.close()

def update_agent_prices(df_all):
    """מעדכן את המחירים הנוכחיים בתיק הסוכנים מתוך הסריקה האחרונה"""
    if df_all.empty: return
    conn = _get_conn()
    cursor = conn.cursor()
    for _, row in df_all.iterrows():
        cursor.execute("UPDATE agent_portfolio SET current_price = ? WHERE symbol = ? AND status = 'OPEN'",
                       (row['Price'], row['Symbol']))
    conn.commit()
    conn.close()

def load_agent_portfolio():
    conn = _get_conn()
    df = pd.read_sql_query("SELECT * FROM agent_portfolio WHERE status = 'OPEN'", conn)
    conn.close()
    if not df.empty:
        # חישוב תשואה באחוזים
        df['Yield_%'] = (df['current_price'] - df['buy_price']) / df['buy_price'] * 100
        df['PnL_$'] = df['current_price'] - df['buy_price']
    return df

def clear_agent_portfolio():
    conn = _get_conn()
    conn.execute("DELETE FROM agent_portfolio")
    conn.commit()
    conn.close()
