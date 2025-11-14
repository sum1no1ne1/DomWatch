import socket
import ssl
from datetime import datetime
import requests
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = ["login", "verify", "secure", "update", "account"]

def is_domain_valid_https(domain, max_redirects=5):    
    hostname = domain
    port = 443

   
    try:
        context = ssl.create_default_context()
        with socket.create_connection((hostname, port), timeout=10) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
    except Exception as e:
        print(f"   - SSL connection failed for {domain}: {e}")
        return False

    try:
        not_after_str = cert['notAfter']
        expiry_date = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
        if datetime.now() >= expiry_date:
            print(f"   - SSL certificate expired for {domain}")
            return False
    except Exception as e:
        print(f"   - Could not verify SSL certificate date for {domain}: {e}")
        return False

   
    try:
        url = f"https://{hostname}"
        redirect_count = 0

        while redirect_count <= max_redirects:
            response = requests.get(url, timeout=10, allow_redirects=False)
            status = response.status_code

            if 200 <= status < 300:
                # Success
                return True

            elif 300 <= status < 400:
                # Redirect
                redirect_count += 1
                redirect_url = response.headers.get("Location")
                if not redirect_url:
                    print(f"   - Redirect with no Location header for {url}")
                    return False

                parsed_original = urlparse(url)
                parsed_redirect = urlparse(redirect_url)

                if parsed_redirect.netloc and parsed_redirect.netloc != parsed_original.netloc:
                    for keyword in SUSPICIOUS_KEYWORDS:
                        if keyword in parsed_redirect.netloc.lower():
                            print(f"   - Suspicious redirect to {redirect_url}")
                            return False

             
                if not parsed_redirect.scheme:
                    redirect_url = f"{parsed_original.scheme}://{parsed_original.netloc}{redirect_url}"

                url = redirect_url

            elif 400 <= status < 500:
                print(f"   - Client error {status} for {url}")
                return False

            elif 500 <= status < 600:
                print(f"   - Server error {status} for {url}")
                return False

            else:
        
                print(f"   - Unexpected status code {status} for {url}")
                return False

        print(f"   - Too many redirects for {domain}")
        return False

    except requests.RequestException as e:
        print(f"   - HTTP request failed for {domain}: {e}")
        return False
