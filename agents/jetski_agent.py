import json
import os
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    # Handle environment where playwright isn't installed yet
    def sync_playwright(): raise ImportError("Playwright is required to use Jetski")

from libs.steel.swarm import Agent

class JetskiBrowserAgent(Agent):
    def __init__(self):
        try:
            self.p = sync_playwright().start()
            # Headless=True for Cloud Run, False for Debugging
            self.browser = self.p.chromium.launch(headless=True) 
            self.page = self.browser.new_page()
            self.dom_cache = {} # Map[Index, ElementHandle]
        except Exception as e:
            print(f"Jetski Boot Warning: {e}. Running in Mock Mode.")
            self.browser = None

    def _get_interactive_elements(self):
        """
        The Magic: Maps raw DOM to clean Indices [1], [2], [3]
        """
        if not self.browser: return "[0] MOCK: Search Button"

        # Find all inputs, buttons, and links
        elements = self.page.query_selector_all("button, input, a, select, [role='button']")
        self.dom_cache = {i: el for i, el in enumerate(elements)}
        
        # Generate the "LLM View"
        dom_text = []
        for i, el in self.dom_cache.items():
            try:
                text = el.inner_text().strip() or el.get_attribute("placeholder") or "Unlabeled"
                tag = el.evaluate("el => el.tagName")
                dom_text.append(f"[{i}] {tag}: {text}")
            except:
                continue
        return "\n".join(dom_text)

    def run(self, task: str) -> str:
        # This is where the LLM Loop would live. 
        # For the "God Mode" prototype, we hardcode the tool execution flow.
        # In prod, this calls Gemini 1.5 Pro with the System Prompt.
        
        # 1. Inject System Prompt (The Soul)
        try:
            system_prompt = open("docs/jetski_protocol.md").read()
        except:
            system_prompt = "Jetski System Prompt Missing"
        
        # 2. Execution (Simulated for this artifacts write)
        return f"🏄 [Jetski] Processed task: {task}. (Browser Agent Ready)"

    # --- THE ARSENAL (Tool Implementations) ---

    def browser_navigate(self, url: str):
        print(f"🏄 Navigating to {url}")
        if self.browser: self.page.goto(url)
    
    def read_browser_page(self):
        return self._get_interactive_elements()

    def browser_click_element(self, index: int):
        if index in self.dom_cache and self.browser:
            print(f"Clicking index [{index}]")
            self.dom_cache[index].click()
        else:
            print(f"❌ Index {index} not found in cache.")

    def capture_browser_screenshot(self, name="state"):
        path = f"browser_artifacts/{name}.png"
        if self.browser:
            os.makedirs("browser_artifacts", exist_ok=True)
            self.page.screenshot(path=path)
            print(f"📸 Screenshot saved: {path}")
