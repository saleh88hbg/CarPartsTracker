import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Optional  # <--- HÄR har vi lagt till Dict och Optional!
from database import PriceHistory

def search_live_prices(keyword: str, oem_number: str = None) -> List[Dict]:
    """
    Söker live-priser på reservdelar från anslutna butiker.
    (Här lägger vi till parsers för Trodo, Autodoc m.fl.)
    """
    query = oem_number if oem_number else keyword
    print(f"🌐 [LIVE SCRAPER] Söker i butiker efter: '{query}'...")

    results = []

    # --- EXEMPEL PÅ STRUKTUR FÖR EN LIVE SCRAPER (Trodo/Mekonomen/Autodoc) ---
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # (Demonstration av datastrukturen vi plockar ut live)
    # T.ex. vi söker på ett sökord och strukturerar träffarna:
    results.append({
        "store_name": "Trodo",
        "price_sek": 389.0,
        "shipping_cost_sek": 69.0,
        "in_stock": True,
        "delivery_days": "2-4 dgr",
        "url": f"https://www.trodo.se/search?q={query}"
    })
    
    results.append({
        "store_name": "Autodoc",
        "price_sek": 412.0,
        "shipping_cost_sek": 99.0,
        "in_stock": True,
        "delivery_days": "3-5 dgr",
        "url": f"https://www.autodoc.se/search?keyword={query}"
    })

    results.append({
        "store_name": "Mekonomen",
        "price_sek": 549.0,
        "shipping_cost_sek": 0.0,  # Fri hämtning i butik
        "in_stock": True,
        "delivery_days": "1-2 dgr",
        "url": f"https://www.mekonomen.se/sok?q={query}"
    })

    return results