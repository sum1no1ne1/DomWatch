import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse

# Define the paths within the Render project directory
CHROME_BINARY_PATH = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"
CHROMEDRIVER_PATH = "/opt/render/project/.render/chromedriver/chromedriver"

def take_screenshot(domain):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--single-process") # Important for Render
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")

    # Set the Chrome binary location
    chrome_options.binary_location = CHROME_BINARY_PATH

    # Create a Service object pointing to the installed ChromeDriver
    service = Service(CHROMEDRIVER_PATH)

    # Pass the service object to webdriver.Chrome
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        # Construct the URL if needed
        parsed_url = urlparse(domain)
        if not parsed_url.scheme:
            url_to_open = f"https://{domain}"
        else:
            url_to_open = domain

        driver.get(url_to_open)

        # Create a safe filename for the screenshot
        safe_name = "".join(c for c in domain if c.isalnum() or c in "._-")
        screenshot_path = f"screenshots/{safe_name}.png"

        # Ensure the screenshots directory exists
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)

        driver.save_screenshot(screenshot_path)
        return f"   - Screenshot saved for {domain} at {screenshot_path}"

    except Exception as e:
        return f"   - Error taking screenshot for {domain}: {e}"
    finally:
        # Ensure the driver session is properly closed
        if driver:
            driver.quit()

# Example usage (uncomment if running this script directly)
# if __name__ == "__main__":
#     result = take_screenshot("example.com")
#     print(result)