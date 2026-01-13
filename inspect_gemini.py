
import os
import time
from playwright.sync_api import sync_playwright

GEMINI_URL = "https://gemini.google.com/app"

def inspect_page(browser_channel="msedge"):
    profile_name = f"{browser_channel}_profile"
    user_data_dir = os.path.join(os.getcwd(), profile_name)
    
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch_persistent_context(
                user_data_dir, 
                headless=False, 
                channel=browser_channel, 
                args=["--disable-blink-features=AutomationControlled", "--start-maximized"],
                ignore_default_args=["--enable-automation"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
        except Exception as e:
            print(f"Failed: {e}")
            return

        page = browser.pages[0] if browser.pages else browser.new_page()
        page.goto(GEMINI_URL)
        time.sleep(5)
        
        # Dump buttons
        buttons = page.locator("button, div[role='button']").all()
        print(f"Found {len(buttons)} buttons/clickable divs")
        
        print("--- Potential Upload Buttons ---")
        for btn in buttons:
            try:
                aria = btn.get_attribute("aria-label")
                text = btn.inner_text()
                if aria and "load" in aria:
                    print(f"Match: Tag={btn.evaluate('el => el.tagName')}, Aria={aria}, Text={text[:20]}")
                if text and "load" in text:
                    print(f"Match: Tag={btn.evaluate('el => el.tagName')}, Aria={aria}, Text={text[:20]}")
            except:
                pass
        
        # Check inputs
        inputs = page.locator("input").all()
        print(f"\nFound {len(inputs)} inputs")
        for inp in inputs:
             try:
                typ = inp.get_attribute("type")
                val = inp.get_attribute("value")
                print(f"Input: Type={typ}, Value={val}")
             except:
                 pass

        print("\nSaving html to debug.html")
        with open("debug.html", "w", encoding="utf-8") as f:
            f.write(page.content())
            
        time.sleep(2)
        # browser.close() # Keep open

if __name__ == "__main__":
    inspect_page()
