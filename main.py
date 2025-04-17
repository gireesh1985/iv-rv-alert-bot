import datetime
import pandas as pd
from nsepython import nse_optionchain_scrapper, nsefetch
import telegram
import asyncio
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Define the log function
def log(msg):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(total=3, backoff_factor=1, status_forcelist=[429, 500, 502, 503, 504])
    session.mount('https://', HTTPAdapter(max_retries=retries))
    return session

async def send_telegram_alert(message, is_error=False):
    try:
        bot = telegram.Bot(token="7005370202:AAHEy3Oixk3nYCARxr8rUlaTN6LCUHeEDlI")
        chat_id = "537459100"
        prefix = "❌ ERROR: " if is_error else "🚨 Alert: "
        await bot.send_message(chat_id=chat_id, text=f"{prefix}{message}")
        log(f"🚨 Telegram alert sent: {message}")
    except Exception as e:
        log(f"❌ Error sending Telegram alert: {str(e)}")

def fetch_iv_rv_data(symbol="NIFTY"):
    try:
        log("🔄 Fetching IV-RV data...")
        session = create_session_with_retries()
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en,gu;q=0.9,hi;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        # Fetch option chain data for IV
        oc_data = nse_optionchain_scrapper(symbol)
        if not oc_data or 'records' not in oc_data:
            error_msg = "Failed to fetch option chain data"
            log(f"❌ {error_msg}")
            asyncio.run(send_telegram_alert(error_msg, is_error=True))
            return None, None

        # Extract IV from ATM strike
        underlying_price = oc_data['records']['underlyingValue']
        strike_prices = [x['strikePrice'] for x in oc_data['records']['data']]
        atm_strike = min(strike_prices, key=lambda x: abs(x - underlying_price))
        for option in oc_data['records']['data']:
            if option['strikePrice'] == atm_strike and 'CE' in option:
                iv = option['CE'].get('impliedVolatility', 0)
                break
        else:
            error_msg = "IV not found for ATM strike"
            log(f"❌ {error_msg}")
            asyncio.run(send_telegram_alert(error_msg, is_error=True))
            return None, None

        # Fetch historical data for RV
        end_date = datetime.datetime.now()
        start_date = end_date - datetime.timedelta(days=30)
        historical_url = (
            f"https://www.nseindia.com/api/historical/cm/equity?symbol={symbol}"
            f"&from={start_date.strftime('%d-%m-%Y')}&to={end_date.strftime('%d-%m-%Y')}"
        )
        historical_data = nsefetch(historical_url)
        if not historical_data or 'data' not in historical_data:
            error_msg = "Failed to fetch historical data"
            log(f"❌ {error_msg}")
            asyncio.run(send_telegram_alert(error_msg, is_error=True))
            return None, None

        df = pd.DataFrame(historical_data['data'])
        df['CH_CLOSING_PRICE'] = df['CH_CLOSING_PRICE'].astype(float)
        returns = df['CH_CLOSING_PRICE'].pct_change().dropna()
        rv = returns.std() * (252 ** 0.5) * 100  # Annualized volatility

        log(f"Fetched IV: {iv:.2f}, RV: {rv:.2f}")
        return iv, rv
    except Exception as e:
        error_msg = f"Error fetching IV/RV data: {str(e)}"
        log(f"❌ {error_msg}")
        asyncio.run(send_telegram_alert(error_msg, is_error=True))
        return None, None

def should_alert(iv, rv, threshold=5):
    try:
        log(f"🔄 Checking if alert conditions are met...")
        if iv is None or rv is None:
            log("⚠️ Missing data, skipping this cycle.")
            return False
        spread = iv - rv
        log(f"IV-RV Spread: {spread:.2f}")
        if spread >= threshold:
            log(f"🔔 Alert condition met! Spread: {spread:.2f} ≥ Threshold: {threshold}")
            return True
        else:
            log(f"ℹ️ Spread too small. No alert. Threshold: {threshold}")
            return False
    except Exception as e:
        log(f"❌ Error in alert check logic: {str(e)}")
        return False

async def send_alert(iv, rv):
    try:
        log(f"🚨 Preparing to send alert for IV={iv}, RV={rv}")
        message = f"IV={iv:.2f}, RV={rv:.2f}, Spread={iv-rv:.2f}"
        await send_telegram_alert(message)
    except Exception as e:
        log(f"❌ Error sending Telegram alert: {str(e)}")

def main():
    log("🔄 Starting IV-RV Scan")
    iv, rv = fetch_iv_rv_data(symbol="NIFTY")
    if iv is None or rv is None:
        log("⚠️ Data fetch failed. Skipping scan cycle.")
        return
    if should_alert(iv, rv, threshold=5):
        asyncio.run(send_alert(iv, rv))
    else:
        log("No alert triggered")
    log("✅ Scan completed.")

if __name__ == "__main__":
    log("🚀 Script started")
    try:
        main()
    except Exception as e:
        log(f"🔥 Critical error in main: {str(e)}")
        asyncio.run(send_telegram_alert(f"Critical error in script: {str(e)}", is_error=True))