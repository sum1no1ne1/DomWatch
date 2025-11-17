import os
import shutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse

def take_screenshot(domain):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")
    
    # Set binary location for Google Chrome (installed in Dockerfile)
    chrome_options.binary_location = "/usr/bin/google-chrome-stable"
    
    # Use ChromeDriver installed in /usr/local/bin/
    service = Service("/usr/local/bin/chromedriver")

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
        driver.set_window_size(1920, 1080)
        
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
