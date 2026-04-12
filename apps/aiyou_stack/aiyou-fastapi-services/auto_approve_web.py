import os

from playwright.sync_api import Error, expect, sync_playwright

# Configuration – read from environment variables
ADMIN_URL = os.getenv("ADMIN_URL")  # e.g. "https://admin.example.com/login"
USERNAME = os.getenv("ADMIN_USERNAME")
PASSWORD = os.getenv("ADMIN_PASSWORD")

# CSS selectors – adjust to match your admin UI
USERNAME_SELECTOR = os.getenv("USERNAME_SELECTOR", "#username")
PASSWORD_SELECTOR = os.getenv("PASSWORD_SELECTOR", "#password")
LOGIN_BUTTON_SELECTOR = os.getenv("LOGIN_BUTTON_SELECTOR", "button[type='submit']")
APPROVE_BUTTON_SELECTOR = os.getenv("APPROVE_BUTTON_SELECTOR", "button:has-text('Approve')")
DASHBOARD_LANDING_SELECTOR = os.getenv("DASHBOARD_LANDING_SELECTOR", "h1:has-text('Dashboard')")

if not all([ADMIN_URL, USERNAME, PASSWORD]):
    raise OSError(
        "ADMIN_URL, ADMIN_USERNAME, and ADMIN_PASSWORD [VAPORIZED_PWD] variables must be set"
    )


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print(f"Navigating to {ADMIN_URL} ...")
            page.goto(ADMIN_URL)
            # Login
            page.fill(USERNAME_SELECTOR, USERNAME)
            page.fill(PASSWORD_SELECTOR, PASSWORD)
            page.click(LOGIN_BUTTON_SELECTOR)
            expect(page.locator(DASHBOARD_LANDING_SELECTOR)).to_be_visible(timeout=10000)
            print("Login successful. Searching for approve buttons...")
            approve_buttons = page.locator(APPROVE_BUTTON_SELECTOR)
            count = approve_buttons.count()
            if count == 0:
                print("No items to approve.")
            else:
                print(f"Found {count} items. Approving...")
                for i in range(count - 1, -1, -1):
                    approve_buttons.nth(i).click()
                    print(f"Approved item {i + 1}/{count}")
                    page.wait_for_timeout(300)
            print("All done.")
        except Error as e:
            print(f"Playwright error: {e}")
        finally:
            browser.close()


if __name__ == "__main__":
    main()
