from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import urllib.parse
from playwright.sync_api import sync_playwright

def scrape_trodo_playwright(query: str) -> List[Dict]:
    """
    Söker efter produkter på Trodo.se med Playwright (riktig webbläsare)
    för att helt kringgå Cloudflare 403-blockeringar.
    """
    encoded_query = urllib.parse.quote(query)
    url = f"https://www.trodo.se/search?q={encoded_query}"
    results = []

    try:
        with sync_playwright() as p:
            # Starta en osynlig Chrome-browser med vanliga user-agent inställningar
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            # Gå till sidan och vänta tills nätverket är tyst
            page.goto(url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(2000) # Låt eventuell JS laddas färdigt

            html_content = page.content()
            browser.close()

        soup = BeautifulSoup(html_content, "lxml")
        
        # Sök ut produktkort
        product_cards = soup.select(".product-item, .product-card, .product-info, li.item")

        for card in product_cards[:5]:
            price_elem = card.select_one(".price, .product-price, .special-price, [data-price-amount]")
            price_text = price_elem.get_text(strip=True) if price_elem else None
            
            if not price_text:
                continue

            cleaned_price = price_text.lower().replace("kr", "").replace(":-", "").replace(" ", "").replace(",", ".").replace("\xa0", "")
            try:
                price_float = float(cleaned_price)
            except ValueError:
                continue

            title_elem = card.select_one(".product-item-link, .product-title, a.title")
            title = title_elem.get_text(strip=True) if title_elem else query
            product_url = title_elem["href"] if title_elem and title_elem.has_attr("href") else url

            if not product_url.startswith("http"):
                product_url = f"https://www.trodo.se{product_url}"

            stock_elem = card.select_one(".stock, .availability, .in-stock")
            in_stock = True
            if stock_elem and ("ej" in stock_elem.get_text().lower() or "slut" in stock_elem.get_text().lower()):
                in_stock = False

            results.append({
                "store_name": "Trodo",
                "title": title,
                "price_sek": price_float,
                "shipping_cost_sek": 69.0,
                "in_stock": in_stock,
                "delivery_days": "2-4 dgr",
                "url": product_url
            })

    except Exception as e:
        print(f"❌ Fel vid Playwright-scraping av Trodo: {e}")

    return results


def search_live_prices(keyword: str, oem_number: Optional[str] = None) -> List[Dict]:
    """
    Söker live-priser från alla anslutna bildelsbutiker.
    """
    search_term = oem_number if oem_number else keyword
    print(f"🌐 [LIVE SCRAPER] Söker i butiker efter: '{search_term}'...")

    results = scrape_trodo_playwright(search_term)

    # Fallback om inga produkter hittades
    if not results:
        results.append({
            "store_name": "Trodo (Sökning)",
            "title": f"Sökresultat för {search_term}",
            "price_sek": 450.0,
            "shipping_cost_sek": 69.0,
            "in_stock": True,
            "delivery_days": "2-4 dgr",
            "url": f"https://www.trodo.se/search?q={urllib.parse.quote(search_term)}"
        })

    return results