"""
JETSKI REALITY VALIDATOR
Combines Selenium Wire (network) + CDP (browser control)
"""

import contextlib
import time

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from seleniumwire import webdriver


class JetskiEngine:
    """Browser-based reality check for n-autoresearch/Kosmos/BioAgents."""

    def __init__(self, headless: bool = True):
        self.headless = headless
        self.driver = None

    def _init_driver(self):
        """Initialize Chrome with network interception."""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument("--headless=new")

        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")

        # Selenium Wire options (mitmproxy backend)
        seleniumwire_options = {
            "disable_encoding": True,  # Get uncompressed responses
            "verify_ssl": False,  # Allow self-signed certs (dev only)
        }

        self.driver = webdriver.Chrome(
            options=chrome_options, seleniumwire_options=seleniumwire_options
        )

    def verify_endpoint(self, url: str, expected_status: int = 200) -> dict:
        """
        Verify an API endpoint returns expected status.
        Captures full request/response cycle.
        """
        if not self.driver:
            self._init_driver()

        print(f"🚤 JETSKI: Testing {url}...")

        try:
            # Clear previous requests
            del self.driver.requests

            # Make request
            self.driver.get(url)

            # Wait for network idle (2 seconds of no activity)
            time.sleep(2)

            # Capture network traffic
            network_log = []
            for request in self.driver.requests:
                network_log.append(
                    {
                        "url": request.url,
                        "method": request.method,
                        "status": request.response.status_code if request.response else None,
                        "headers": dict(request.headers),
                        "body_size": len(request.response.body) if request.response else 0,
                    }
                )

            # Check main request
            main_request = [r for r in self.driver.requests if url in r.url]
            if not main_request:
                return {
                    "success": False,
                    "error": "No matching request found",
                    "network_log": network_log,
                }

            actual_status = main_request[0].response.status_code

            return {
                "success": actual_status == expected_status,
                "expected_status": expected_status,
                "actual_status": actual_status,
                "network_log": network_log[:10],  # Limit to first 10 requests
                "total_requests": len(self.driver.requests),
            }

        except Exception as e:
            return {"success": False, "error": str(e), "network_log": []}

    def verify_page_render(self, url: str, selector: str) -> dict:
        """
        Verify a page renders correctly and element exists.
        Returns screenshot as base64.
        """
        if not self.driver:
            self._init_driver()

        print(f"🚤 JETSKI: Rendering {url}...")

        try:
            self.driver.get(url)

            # Wait for element (max 10 seconds)
            wait = WebDriverWait(self.driver, 10)
            element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))

            # Capture console logs (errors)
            logs = self.driver.get_log("browser")
            errors = [log for log in logs if log["level"] == "SEVERE"]

            # Take screenshot
            screenshot = self.driver.get_screenshot_as_base64()

            return {
                "success": True,
                "element_found": element is not None,
                "element_text": element.text[:100] if element else None,
                "console_errors": errors,
                "screenshot": screenshot[:500] + "..."
                if screenshot
                else None,  # Truncate for logging
            }

        except Exception as e:
            # Capture screenshot even on failure
            screenshot = None
            with contextlib.suppress(BaseException):
                screenshot = self.driver.get_screenshot_as_base64()

            return {
                "success": False,
                "error": str(e),
                "screenshot": screenshot[:500] + "..." if screenshot else None,
            }

    def intercept_and_modify(self, url: str, modifications: dict) -> dict:
        """
        Advanced: Modify requests/responses in-flight.
        Use case: Test how app handles modified API responses.
        """
        if not self.driver:
            self._init_driver()

        print(f"🚤 JETSKI: Intercepting {url}...")

        def interceptor(request):
            """Modify requests matching pattern."""
            if modifications.get("block_pattern") in request.url:
                request.abort()  # Block request entirely
            elif modifications.get("modify_headers"):
                for key, value in modifications["modify_headers"].items():
                    request.headers[key] = value

        self.driver.request_interceptor = interceptor

        try:
            self.driver.get(url)
            time.sleep(2)

            return {
                "success": True,
                "intercepted_count": len(
                    [
                        r
                        for r in self.driver.requests
                        if modifications.get("block_pattern", "") in r.url
                    ]
                ),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def cleanup(self):
        """Close browser and free resources."""
        if self.driver:
            self.driver.quit()
            self.driver = None


# Singleton instance for Cloud Run
_jetski_instance: JetskiEngine | None = None


def get_jetski() -> JetskiEngine:
    """Get or create singleton Jetski instance."""
    global _jetski_instance
    if _jetski_instance is None:
        _jetski_instance = JetskiEngine(headless=True)
    return _jetski_instance
