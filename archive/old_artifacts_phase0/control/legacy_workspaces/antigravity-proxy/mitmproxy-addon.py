"""
MITM Proxy addon for intercepting Google Antigravity API calls
and replacing the API key with your own.

Usage:
    mitmproxy -s mitmproxy-addon.py

    Then launch Antigravity with:
    HTTP_PROXY=http://localhost:8080 \
    HTTPS_PROXY=http://localhost:8080 \
    /Applications/Antigravity.app/Contents/MacOS/Antigravity
"""

import os
import re

from dotenv import load_dotenv
from mitmproxy import http

# Load environment variables
load_dotenv()

# Your Gemini API key
YOUR_API_KEY = os.getenv("GEMINI_API_KEY", "YOUR_API_KEY_HERE")

# Statistics
stats = {
    "requests_intercepted": 0,
    "keys_replaced": 0,
}


class AntigravityInterceptor:
    def __init__(self):
        print("\n" + "=" * 60)
        print("🚀 Antigravity Proxy - MITM Interceptor")
        print("=" * 60)
        print(f"🔑 Using API Key: {YOUR_API_KEY[:15]}***")
        print("🎯 Target: generativelanguage.googleapis.com")
        print("=" * 60 + "\n")

    def request(self, flow: http.HTTPFlow) -> None:
        """Intercept and modify requests"""

        # Only intercept Gemini API requests
        if "generativelanguage.googleapis.com" not in flow.request.pretty_host:
            return

        stats["requests_intercepted"] += 1

        print(f"\n📥 INCOMING REQUEST #{stats['requests_intercepted']}")
        print(f"   Method: {flow.request.method}")
        print(f"   URL: {flow.request.url}")

        # Extract original key
        original_key = None

        # Replace API key in header
        if "x-goog-api-key" in flow.request.headers:
            original_key = flow.request.headers["x-goog-api-key"]
            flow.request.headers["x-goog-api-key"] = YOUR_API_KEY
            stats["keys_replaced"] += 1
            print("   🔄 Replaced key in header")
            print(f"      Old: {original_key[:15]}***")
            print(f"      New: {YOUR_API_KEY[:15]}***")

        # Replace API key in query parameter
        if "key=" in flow.request.url:
            match = re.search(r"key=([^&]+)", flow.request.url)
            if match:
                if not original_key:
                    original_key = match.group(1)
                flow.request.url = re.sub(
                    r"key=[^&]+", f"key={YOUR_API_KEY}", flow.request.url
                )
                stats["keys_replaced"] += 1
                print("   🔄 Replaced key in URL")
                print(f"      Old: {original_key[:15]}***")
                print(f"      New: {YOUR_API_KEY[:15]}***")

        # Log request body preview (first 200 chars)
        if flow.request.content:
            try:
                body_preview = flow.request.content.decode("utf-8")[:200]
                print(f"   📄 Body preview: {body_preview}...")
            except:
                print("   📄 Body: <binary data>")

    def response(self, flow: http.HTTPFlow) -> None:
        """Log responses"""

        # Only log Gemini API responses
        if "generativelanguage.googleapis.com" not in flow.request.pretty_host:
            return

        status_icon = "✅" if flow.response.status_code == 200 else "❌"
        print(f"\n{status_icon} RESPONSE")
        print(f"   Status: {flow.response.status_code}")

        if flow.response.status_code != 200:
            print("   ⚠️  Non-200 response!")
            try:
                error_preview = flow.response.content.decode("utf-8")[:300]
                print(f"   Error: {error_preview}")
            except:
                pass

        # Print statistics
        print(
            f"\n📊 Stats: {stats['requests_intercepted']} requests, {stats['keys_replaced']} keys replaced"
        )
        print("=" * 60)


# Create addon instance
addons = [AntigravityInterceptor()]
