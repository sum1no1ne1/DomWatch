def check(domain):
    tlds = [
    ".com", ".org", ".net", ".int", ".edu", ".gov", ".mil",
    ".io", ".ai", ".co", ".tech", ".biz", ".info", ".me",
    ".app", ".dev", ".xyz", ".online", ".shop", ".site", ".in",
    ".cloud", ".store", ".blog", ".design", ".art", ".media",
    ".digital", ".solutions", ".agency", ".studio", ".global",
    ".company", ".space", ".world", ".website", ".live", ".us",
    ".uk", ".ca", ".au", ".de", ".fr", ".jp", ".sg"
]
    try:
        if not domain.startswith("www."):
            return False
        for tld in tlds:
            if domain.endswith(tld):
                return True
                break 
        return False  
    except Exception as e:
        print(f"error:{e}")  