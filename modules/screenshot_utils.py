import os
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.binary_location = os.environ.get("CHROME_BIN", "/usr/bin/chromium")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    service = Service(os.environ.get("CHROMEDRIVER_PATH", "/usr/bin/chromedriver"))
    return webdriver.Chrome(service=service, options=chrome_options)
   
   
    # chrome_options = Options()
    
    # # For local testing - remove render-specific options
    # chrome_options.add_argument("--headless=new")  # Keep this for headless mode
    # chrome_options.add_argument("--no-sandbox")
    # chrome_options.add_argument("--disable-dev-shm-usage")
    # chrome_options.add_argument("--disable-gpu")
    # chrome_options.add_argument("--window-size=1920,1080")
    
    # Remove the render-specific binary location
    # Let Selenium find Chrome automatically or specify local path
    service = Service()  # This will look for chromedriver in PATH
    
    # Alternative: If you have chromedriver in a specific location locally:
    # service = Service("/path/to/your/chromedriver")  # Update with your local path
    
    return webdriver.Chrome(service=service, options=chrome_options)
def take_screenshot(domain):
    driver = get_chrome_driver()
    try:
        url_to_open = domain if urlparse(domain).scheme else f"https://{domain}"
        driver.get(url_to_open)

        safe_name = "".join(c for c in domain if c.isalnum() or c in "._-")
        os.makedirs("screenshots", exist_ok=True)
        path = f"screenshots/{safe_name}.png"
        driver.save_screenshot(path)
        return f"✔ Screenshot saved for {domain} at {path}"
    except Exception as e:
        return f"✘ Error taking screenshot for {domain}: {e}"
    finally:
        driver.quit()
