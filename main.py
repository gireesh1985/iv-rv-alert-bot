import time
import datetime

# Define the log function at the start of the script
def log(msg):
    print(f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {msg}")

def fetch_iv_rv_data():
    try:
        log("🔄 Fetching IV-RV data...")  # Log to confirm fetching data is triggered
        # Replace with your actual IV/RV fetching logic
        iv = 22.5  # Placeholder
        rv = 17.8  # Placeholder
        log(f"Fetched IV: {iv}, RV: {rv}")  # Log fetched data
        return iv, rv
    except Exception as e:
        log(f"❌ Error fetching IV/RV data: {e}")
        return None, None

def should_alert(iv, rv, threshold=5):
    try:
        log(f"🔄 Checking if alert conditions are met...")  # Log when checking alert conditions
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
        log(f"❌ Error in alert check logic: {e}")
        return False

def send_alert(iv, rv):
    try:
        log(f"🚨 Preparing to send alert for IV={iv}, RV={rv}")  # Log when preparing alert
        # Replace with actual Telegram or email logic
        log(f"🚨 Sending Alert: IV={iv}, RV={rv}")
    except Exception as e:
        log(f"❌ Error sending alert: {e}")

def main():
    log("🔄 Starting IV-RV Scan")
    iv, rv = fetch_iv_rv_data()
    if iv is None or rv is None:
        log("⚠️ Data fetch failed. Skipping scan cycle.")
        return  # Skip processing if no data

    if should_alert(iv, rv, threshold=5):
        send_alert(iv, rv)
    else:
        log("No alert triggered")
    log("✅ Scan completed.\n")

if __name__ == "__main__":
    while True:
        try:
            log("🔄 Running main loop")
            main()
            # Wait before next scan (optional: Render restarts anyway)
            time.sleep(60 * 15)  # 15 min wait if run as loop
        except Exception as e:
            log(f"🔥 Critical error in main loop: {e}")
            time.sleep(60)

