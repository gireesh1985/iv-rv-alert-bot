def fetch_iv_rv_data():
    try:
        # Replace with actual fetching logic; this is a placeholder
        iv = 22.5  # Placeholder (update with live data fetching logic)
        rv = 17.8  # Placeholder (update with live data fetching logic)
        
        # Debug log
        log(f"Fetched IV: {iv}, RV: {rv}")
        
        return iv, rv
    except Exception as e:
        log(f"❌ Error fetching IV/RV data: {e}")
        return None, None

def should_alert(iv, rv, threshold=5):
    try:
        if iv is None or rv is None:
            log("⚠️ Missing data, skipping this cycle.")
            return False

        # Calculate IV-RV spread
        spread = iv - rv
        log(f"IV-RV Spread: {spread:.2f}")

        if spread >= threshold:
            log(f"🔔 Alert condition met! Spread: {spread:.2f} ≥ Threshold: {threshold}")
            return True
        else:
            log(f"ℹ️ Spread too small. No alert. Spread: {spread:.2f}, Threshold: {threshold}")
            return False
    except Exception as e:
        log(f"❌ Error in alert check logic: {e}")
        return False

def main():
    log("🔄 Starting IV-RV Scan")
    iv, rv = fetch_iv_rv_data()
    if iv is not None and rv is not None:
        if should_alert(iv, rv, threshold=5):
            send_alert(iv, rv)
        else:
            log("No alert triggered")
    else:
        log("Data fetch failed, no alert.")
    log("✅ Scan completed.\n")

if __name__ == "__main__":
    while True:
        try:
            main()
            time.sleep(60 * 15)  # 15 min wait (adjust timing as needed)
        except Exception as e:
            log(f"🔥 Critical error in main loop: {e}")
            time.sleep(60)
