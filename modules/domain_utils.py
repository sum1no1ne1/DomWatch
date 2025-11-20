import socket
import ssl
from datetime import datetime
import requests
from urllib.parse import urlparse

SUSPICIOUS_KEYWORDS = ["login", "verify", "secure", "update", "account"]
PARKING_INDICATORS = [
    "domain", "parked", "buy", "purchase", "register", "available", 
    "sale", "auction", "marketplace", "website", "hosting", "name"
]

def is_domain_valid_https_with_reason(domain, max_redirects=5):    
    hostname = domain
    port = 443
    clean_hostname = hostname.replace('www.', '')
    
    # SSL connection check
    try:
        context = ssl.create_default_context()
        with socket.create_connection((clean_hostname, port), timeout=20) as sock:
            with context.wrap_socket(sock, server_hostname=clean_hostname) as ssock:
                cert = ssock.getpeercert()
    except socket.gaierror:
        return False, f"DNS lookup failed: Host {clean_hostname} not found"
    except ssl.SSLError as e:
        return False, f"SSL error: {str(e)}"
    except socket.timeout:
        return False, "Connection timeout"
    except Exception as e:
        return False, f"SSL connection failed: {str(e)}"

    # Certificate expiry check
    try:
        not_after_str = cert['notAfter']
        expiry_date = datetime.strptime(not_after_str, '%b %d %H:%M:%S %Y %Z')
        if datetime.now() >= expiry_date:
            return False, "SSL certificate expired"
    except Exception as e:
        return False, f"Could not verify SSL certificate date: {str(e)}"

    # HTTP request check - follow redirects manually to control count
    try:
        url = f"https://{hostname}"
        redirect_count = 0
        current_url = url

        # Manually follow redirects up to max_redirects
        while redirect_count <= max_redirects:
            try:
                response = requests.get(current_url, timeout=10, allow_redirects=False)
            except requests.exceptions.Timeout:
                return False, "HTTP request timeout"
            except requests.exceptions.ConnectionError:
                return False, "Connection error"
            except requests.exceptions.RequestException as e:
                return False, f"HTTP request error: {str(e)}"
                
            status = response.status_code

            if 200 <= status < 300:
                # We've reached the final destination, now check if it's parked
                final_response = requests.get(current_url, timeout=10)
                
                # Check final URL
                final_url = final_response.url
                final_domain = urlparse(final_url).netloc.lower()
                
                # Check if final destination is a parking service
                parking_domains = [
                    "sedoparking.com", "parkingcrew.net", "trafficjunky.net", 
                    "sedo.com", "afternic.com", "park.io", "parked.com",
                    "domainmarket.com", "buydomains.com", "domainname.com",
                    "sedoleads.com", "parkingpage.name", "domainbroker.com"
                ]
                
                if any(parking_domain in final_domain for parking_domain in parking_domains):
                    return False, "Redirects to domain parking service"
                
                # Check content for parking indicators
                content = final_response.text.lower()
                parking_phrases = [
                    "this domain is for sale", "buy this domain", "purchase this domain",
                    "domain for sale", "register this domain", "available now",
                    "parked page", "domain parking", "domain marketplace",
                    "click here to buy", "make an offer", "buy it now",
                    "interested in this domain", "inquire about this domain", "domain auction"
                ]
                
                if any(phrase in content for phrase in parking_phrases):
                    return False, "Domain appears to be parked"
                
                # Check if the final domain is different from original and suspicious
                original_domain = hostname.lower()
                if final_domain != original_domain and not final_domain.endswith(original_domain):
                    return False, f"Redirected to different domain: {final_url}"
                
                return True, "Success"
            elif 300 <= status < 400:
                redirect_count += 1
                redirect_url = response.headers.get("Location")
                if not redirect_url:
                    return False, "Redirect with no Location header"
                
                parsed_original = urlparse(current_url)
                parsed_redirect = urlparse(redirect_url)

                if parsed_redirect.netloc and parsed_redirect.netloc != parsed_original.netloc:
                    for keyword in SUSPICIOUS_KEYWORDS:
                        if keyword in parsed_redirect.netloc.lower():
                            return False, f"Suspicious redirect to {redirect_url}"
                    
                    # Check if redirect is to domain parking service
                    redirect_lower = parsed_redirect.netloc.lower()
                    parking_domains = ["sedoparking.com", "parkingcrew.net", "trafficjunky.net", 
                                      "sedo.com", "afternic.com", "park.io", "bit.ly", "tinyurl.com"]
                    
                    if any(parking_domain in redirect_lower for parking_domain in parking_domains):
                        return False, "Redirects to domain parking service"
                
                if not parsed_redirect.scheme:
                    redirect_url = f"{parsed_original.scheme}://{parsed_original.netloc}{redirect_url}"
                current_url = redirect_url
            elif 400 <= status < 500:
                status_text = requests.status_codes._codes.get(status, ['Unknown'])[0] if status in requests.status_codes._codes else 'Unknown client error'
                return False, f"Client error {status}: {status_text}"
            elif 500 <= status < 600:
                status_text = requests.status_codes._codes.get(status, ['Unknown'])[0] if status in requests.status_codes._codes else 'Unknown server error'
                return False, f"Server error {status}: {status_text}"
            else:
                return False, f"Unexpected status code {status}"

        return False, "Too many redirects"
    except requests.RequestException as e:
        return False, f"HTTP request failed: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"