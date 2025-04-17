import time
import datetime
import os

def log(msg):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}", flush=True)

def fetch_iv_rv_data():
    try:
        log("🔄 Fetching IV-RV data...")
        # Replace with actual fetching logic
        iv = 25.0  # Test value to trigger alert
        rv = 18.0  # Test value to trigger alert
        log(f"Fetched IV: {iv}, RV: {rv}")
        return iv, rv
    except Exception as e:
        log(f"❌ Error fetching IV/RV data: {str(e)}")
        raise  # Raise for debugging

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

def send_alert(iv, rv):
    try:
        log(f"🚨 Preparing to send alert for IV={iv}, RV={rv}")
        # Replace with actual alert logic (e.g., Telegram)
        log(f"🚨 Sending Alert: IV={iv}, RV={rv}")
    except Exception as e:
        log(f"❌ Error sending alert: {str(e)}")

def main():
    log("🔄 Starting IV-RV Scan")
    iv, rv = fetch_iv_rv_data()
    if iv is None or rv is None:
        log("⚠️ Data fetch failed. Skipping scan cycle.")
        return
    if should_alert(iv, rv, threshold=5):
        send_alert(iv, rv)
    else:
        log("No alert triggered")
    log("✅ Scan completed.\n")

if __name__ == "__main__":
    log("🚀 Script started")
    while True:
        try:
            log("🔄 Running main loop")
            main()
            time.sleep(60 * 15)  # 15 min wait
        except Exception as e:
            log(f"🔥 Critical error in main loop: {str(e)}")
            time.sleep(60)
