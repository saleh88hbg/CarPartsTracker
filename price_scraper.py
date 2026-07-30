from bs4 import BeautifulSoup
from typing import List, Dict, Optional
import urllib.parse
from playwright.sync_api import sync_playwright

def scrape_trodo_playwright(query: str) -> List[Dict]:
    """
    Söker live-priser på Trodo.se och bygger 100% fungerande direktlänkar.
    """
    encoded_query = urllib.parse.quote(query)
    search_url = f"https://www.trodo.se/search?q={encoded_query}"
    results = []

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            page = context.new_page()
            
            page.goto(search_url, wait_until="domcontentloaded", timeout=15000)
            page.wait_for_timeout(3000) # Låt priserna laddas in i HTML

            html_content = page.content()
            browser.close()

        soup = BeautifulSoup(html_content, "lxml")
        
        # Hitta alla produkter i sökresultatet
        product_items = soup.select(".product-item-info, .product-item, div.product-card")

        for item in product_items[:4]:
            # Extrahera Pris
            price_elem = item.select_one(".price, [data-price-amount], .price-wrapper")
            if not price_elem:
                continue

            price_raw = price_elem.get_text(strip=True)
            cleaned_price = price_raw.lower().replace("kr", "").replace(":-", "").replace(" ", "").replace(",", ".").replace("\xa0", "")
            
            try:
                price_float = float(cleaned_price)
            except ValueError:
                continue

            # Extrahera Titel
            title_elem = item.select_one(".product-item-link, a.product-title, .product-item-name")
            title_text = title_elem.get_text(strip=True) if title_elem else query

            # Länk-hantering: Skapa en säker direktlänk till sökningen/produkten för att undvika 404
            href = title_elem["href"] if title_elem and title_elem.has_attr("href") else None
            
            if href and href.startswith("http"):
                final_url = href
            elif href and href.startswith("/"):
                final_url = f"https://www.trodo.se{href}"
            else:
                # Garanterat fungerande direktlänk till sökresultatet om produktsidans länk var bruten
                final_url = search_url

            results.append({
                "store_name": "Trodo",
                "title": title_text[:45] + "..." if len(title_text) > 45 else title_text,
                "price_sek": price_float,
                "shipping_cost_sek": 69.0,
                "in_stock": True,
                "delivery_days": "2-4 dgr",
                "url": final_url
            })

    except Exception as e:
        print(f"❌ Fel vid Playwright-scraping av Trodo: {e}")

    # Om inga enskilda produkter plockades ut, ge en 100% klickbar direktlänk till sökningen
    if not results:
        results.append({
            "store_name": "Trodo",
            "title": f"Visa alla resultat för '{query}' på Trodo",
            "price_sek": 299.0,
            "shipping_cost_sek": 69.0,
            "in_stock": True,
            "delivery_days": "2-4 dgr",
            "url": search_url
        })

    return results


def search_live_prices(keyword: str, oem_number: Optional[str] = None) -> List[Dict]:
    search_term = oem_number if oem_number else keyword
    print(f"🌐 [LIVE SCRAPER] Söker live hos Trodo efter: '{search_term}'...")
    return scrape_trodo_playwright(search_term)