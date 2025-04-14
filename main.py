
import requests
import time
from bs4 import BeautifulSoup
import pandas as pd

# Telegram Credentials
BOT_TOKEN = "7005370202:AAHEy3Oixk3nYCARxr8rUlaTN6LCUHeEDlI"
CHAT_ID = "537459100"

def send_telegram_alert(message):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    data = {"chat_id": CHAT_ID, "text": message}
    try:
        requests.post(url, data=data)
    except Exception as e:
        print("Telegram Error:", e)

def fetch_iv(symbol):
    url = f"https://www.nseindia.com/api/option-chain-indices?symbol={symbol}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }
    with requests.Session() as s:
        try:
            s.get("https://www.nseindia.com", headers=headers, timeout=5)
            response = s.get(url, headers=headers, timeout=5)
            data = response.json()
            iv_list = []
            for record in data["records"]["data"]:
                if "CE" in record and record["CE"].get("impliedVolatility"):
                    iv_list.append(record["CE"]["impliedVolatility"])
                if "PE" in record and record["PE"].get("impliedVolatility"):
                    iv_list.append(record["PE"]["impliedVolatility"])
            return round(sum(iv_list)/len(iv_list), 2) if iv_list else None
        except:
            return None

def fetch_realized_vol(symbol):
    try:
        url = f"https://www.niftytrader.in/option-chain/{symbol.lower()}"
        r = requests.get(url, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        tables = soup.find_all("table")
        for table in tables:
            if "Realized Volatility" in table.text:
                df = pd.read_html(str(table))[0]
                if "Realized Volatility" in df.columns:
                    rv = df["Realized Volatility"].iloc[0]
                    return float(rv.strip('%')) if isinstance(rv, str) else float(rv)
    except:
        return None

def scan_iv_rv(symbol):
    iv = fetch_iv(symbol)
    rv = fetch_realized_vol(symbol)
    if iv is not None and rv is not None:
        spread = iv - rv
        if spread >= 2:
            message = f"⚠️ {symbol} ALERT\nIV: {iv}%\nRV: {rv}%\nSpread: {spread:.2f}%"
            print(message)
            send_telegram_alert(message)

def main():
    while True:
        print("🔄 Scanning IV-RV...")
        scan_iv_rv("NIFTY")
        scan_iv_rv("BANKNIFTY")
        time.sleep(300)

if __name__ == "__main__":
    main()
