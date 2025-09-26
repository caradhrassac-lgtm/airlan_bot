import os, requests
from typing import List, Dict

API_KEY = os.getenv("GOOGLE_CSE_KEY", "")
CX = os.getenv("GOOGLE_CSE_CX", "")

def google_search(query: str, num: int = 10) -> List[Dict]:
    if not API_KEY or not CX:
        raise RuntimeError("Missing GOOGLE_CSE_KEY or GOOGLE_CSE_CX environment variables.")
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "key": API_KEY,
        "cx": CX,
        "q": query,
        "num": min(max(num, 1), 10),
        "safe": "off",
        "hl": "es",
    }
    r = requests.get(url, params=params, timeout=30)
    r.raise_for_status()
    return r.json().get("items", [])
