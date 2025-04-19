def fetch_nse_cookies(headers):
    try:
        log("🔄 Attempting to fetch cookies with cloudscraper...")
        scraper = cloudscraper.create_scraper(
            browser={
                'browser': 'chrome',
                'platform': 'windows',
                'mobile': False
            },
            delay=10,
            request_timeout=30  # Increased timeout
        )
        response = scraper.get("https://www.nseindia.com", headers=headers, timeout=30)
        log(f"Cloudscraper response: HTTP {response.status_code}, Content-Length: {len(response.content)}")
        if response.status_code == 200 and response.cookies:
            session = create_session_with_retries()
            session.cookies.update(response.cookies)
            log(f"✅ Successfully fetched cookies with cloudscraper")
            return session
        log("❌ Cloudscraper failed, falling back to Playwright")
    except Exception as e:
        log(f"❌ Cloudscraper error: {str(e)}, falling back to Playwright")

    try:
        log("🔄 Attempting to fetch cookies with Playwright...")
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(**{
                "user_agent": headers['User-Agent'],
                "viewport": {"width": 1280, "height": 720}
            })
            page = context.new_page()
            page.goto("https://www.nseindia.com", timeout=60000)  # Increased timeout
            if page.url == "https://www.nseindia.com":
                cookies = context.cookies()
                session = create_session_with_retries()
                for cookie in cookies:
                    session.cookies.set(cookie['name'], cookie['value'], domain=cookie['domain'], path=cookie['path'])
                log(f"✅ Playwright fetched {len(cookies)} cookies")
                browser.close()
                return session
            else:
                log(f"❌ Playwright redirected to {page.url}")
                browser.close()
                return None
    except Exception as e:
        log(f"❌ Playwright error: {str(e)}")
        return None