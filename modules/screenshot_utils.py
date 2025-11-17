import os
import platform
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from urllib.parse import urlparse

def get_chrome_driver():
    chrome_options = Options()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    system = platform.system()

    if system == "Linux":
        # Render / Linux Docker
        chrome_options.binary_location = "/usr/bin/chromium"
        service = Service("/usr/bin/chromedriver")

    elif system == "Windows":
        # Local Windows
        # Make sure to download ChromeDriver from https://chromedriver.chromium.org/downloads
        # and place it somewhere, e.g., C:/chromedriver.exe
        driver_path = os.environ.get("CHROMEDRIVER_PATH", "C:/chromedriver.exe")
        service = Service(driver_path)

    elif system == "Darwin":
        # Local macOS
        # Make sure chromedriver is installed via brew or manually: /usr/local/bin/chromedriver
        driver_path = os.environ.get("CHROMEDRIVER_PATH", "/usr/local/bin/chromedriver")
        chrome_options.binary_location = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        service = Service(driver_path)

    else:
        raise Exception(f"Unsupported OS: {system}")

    return webdriver.Chrome(service=service, options=chrome_options)


def take_screenshot(domain):
    driver = get_chrome_driver()
    try:
        parsed_url = urlparse(domain)
        url_to_open = domain if parsed_url.scheme else f"https://{domain}"

        driver.get(url_to_open)

        safe_name = "".join(c for c in domain if c.isalnum() or c in "._-")
        screenshot_path = f"screenshots/{safe_name}.png"

        os.makedirs(os.path.dirname(screenshot_path), exist_ok=True)
        driver.save_screenshot(screenshot_path)

        return f"✔ Screenshot saved for {domain} at {screenshot_path}"

    except Exception as e:
        return f"✘ Error taking screenshot for {domain}: {e}"

    finally:
        driver.quit()


# Manual test
# if __name__ == "__main__":
#     print(take_screenshot("example.com"))
