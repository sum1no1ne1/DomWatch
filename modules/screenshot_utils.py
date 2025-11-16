import os
import shutil # Import shutil if you plan to use it later (e.g., for cleanup)
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service  # Import Service
from urllib.parse import urlparse
from webdriver_manager.chrome import ChromeDriverManager # Import ChromeDriverManager

def take_screenshot(domain):
    # Configure Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--remote-debugging-port=9222")
    
    # Try different possible Chrome/Chromium binary locations
    possible_paths = [
        "/usr/bin/chromium-browser",  # Common on Debian/Ubuntu
        "/usr/bin/chromium",          # Alternative location
        "/usr/bin/google-chrome",     # Google Chrome on Linux
        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # macOS
        "C:/Program Files/Google/Chrome/Application/chrome.exe",         # Windows
        "C:/Program Files (x86)/Google/Chrome/Application/chrome.exe"    # Windows (32-bit)
    ]
    
    # Find the first available Chrome binary
    chrome_binary_path = None
    for path in possible_paths:
        if os.path.exists(path):
            chrome_binary_path = path
            break
    
    # If no binary found, raise an error
    if chrome_binary_path:
        chrome_options.binary_location = chrome_binary_path
    else:
        # If running in a container environment like Render, try without specifying
        # Or install chromium-browser first
        pass
    
    # Create a Service object using ChromeDriverManager
    # This ensures the correct driver executable is found and managed
    service = Service(ChromeDriverManager().install())

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

# Example usage (uncomment if running this script directly)
# if __name__ == "__main__":
#     result = take_screenshot("example.com")
#     print(result)