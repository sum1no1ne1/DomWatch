import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service 
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager 

def take_screenshot(domain):
 
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
   
    service = Service(ChromeDriverManager().install())

    
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
       
        parsed_url = urlparse(domain)
        if not parsed_url.scheme:
            url_to_open = f"https://{domain}"
        else:
            url_to_open = domain
            
        driver.get(url_to_open)
        driver.set_window_size(1920, 1080)
        
        
        safe_name = "".join(c for c in domain if c.isalnum() or c in "._-")
        screenshot_path = f"screenshots/{safe_name}.png"
        
        
        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        
        driver.save_screenshot(screenshot_path)
        return f"   - Screenshot saved for {domain} at {screenshot_path}"
        
    except Exception as e:
        return f"   - Error taking screenshot for {domain}: {e}"
    finally:
       
        if driver:
            driver.quit()

