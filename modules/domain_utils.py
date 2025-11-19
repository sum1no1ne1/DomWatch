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
        with socket.create_connection((clean_hostname, port), timeout=10) as sock:
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

    # HTTP request check - follow redirects to check final destination
    try:
        url = f"https://{hostname}"
        
        # Make a request that follows redirects to see where it ends up
        final_response = requests.get(url, timeout=10, allow_redirects=True, max_redirects=max_redirects)
        
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
        
        # If we got here, it's a valid working domain
        return True, "Success"
        
    except requests.exceptions.Timeout:
        return False, "HTTP request timeout"
    except requests.exceptions.ConnectionError:
        return False, "Connection error"
    except requests.exceptions.TooManyRedirects:
        return False, "Too many redirects"
    except requests.exceptions.RequestException as e:
        return False, f"HTTP request error: {str(e)}"
    except Exception as e:
        return False, f"Unexpected error: {str(e)}"