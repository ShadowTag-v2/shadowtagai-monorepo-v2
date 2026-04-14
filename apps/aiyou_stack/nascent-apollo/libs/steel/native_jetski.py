from playwright.sync_api import sync_playwright

try:
    from playwright_stealth import stealth_sync

    STEALTH_AVAILABLE = True
except ImportError:
    STEALTH_AVAILABLE = False
import logging

logger = logging.getLogger("NativeJetski")


class NativeJetski:
    """The 'Clean' Jetski: Connects to a native browser instance via CDP.
    Bypasses extension detection by behaving like a standard debugger.
    Augmented with pip install playwright-stealth.
    """

    def __init__(self, cdp_url="http://localhost:9222"):
        self.cdp_url = cdp_url

    def navigate(self, url):
        try:
            with sync_playwright() as p:
                logger.info(f"🚤 NATIVE JETSKI: Connecting to CDP at {self.cdp_url}...")
                browser = p.chromium.connect_over_cdp(self.cdp_url)

                if not browser.contexts:
                    return "❌ No browser context found. Is Brave running?"

                context = browser.contexts[0]
                if not context.pages:
                    page = context.new_page()
                else:
                    page = context.pages[0]

                # APPLY STEALTH
                if STEALTH_AVAILABLE:
                    stealth_sync(page)
                    logger.info("🥷 Stealth Mode: ENGAGED")
                else:
                    logger.warning("⚠️ Stealth Mode: UNAVAILABLE (pip install playwright-stealth)")

                logger.info(f"Navigate: {url}")
                page.goto(url)
                title = page.title()

                return f"✅ Navigated to [{title}]({url})"
        except Exception as e:
            logger.error(f"💥 CDP Error: {e}")
            return f"Error: {e}"


if __name__ == "__main__":
    # Test stub
    jet = NativeJetski()
    print(jet.navigate("https://console.cloud.google.com"))
