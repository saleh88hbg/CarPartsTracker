import requests
import re
from bs4 import BeautifulSoup
from typing import Optional
from database import Vehicle

def fetch_vehicle_by_reg(reg_number: str) -> Optional[Vehicle]:
    """
    Hämtar märke, modell, år, färg, drivmedel, växellåda och senast besiktigade miltal.
    """
    clean_reg = reg_number.strip().upper().replace(" ", "").replace("-", "")
    
    if len(clean_reg) != 6:
        print(f"❌ Felaktigt registreringsnummer: {reg_number}")
        return None

    print(f"🌐 [LIVE BIL-SÖK] Hämtar fordonsdata för {clean_reg}...")

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36",
        "Accept-Language": "sv-SE,sv;q=0.9,en-US;q=0.8"
    }

    try:
        url = f"https://biluppgifter.se/fordon/{clean_reg}"
        resp = requests.get(url, headers=headers, timeout=8)

        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            page_text = soup.get_text()
            
            # 1. Rubrik / Titel (Märke, Modell, År)
            title_tag = soup.find("title")
            raw_title = title_tag.get_text(strip=True) if title_tag else ""

            make = "Bil"
            model = f"Reg: {clean_reg}"
            year = 2018

            if raw_title and "sök" not in raw_title.lower():
                clean_title = raw_title.split("-")[0].replace("Information om", "").strip()
                words = [w for w in clean_title.split() if w.upper().replace("(", "").replace(")", "") != clean_reg]

                if len(words) >= 1:
                    make = words[0].capitalize()
                    model = " ".join(words[1:3]) if len(words) > 1 else "Modell"
                    
                    for w in words:
                        w_clean = w.replace(",", "").replace("(", "").replace(")", "").strip()
                        if w_clean.isdigit() and len(w_clean) == 4 and (w_clean.startswith("19") or w_clean.startswith("20")):
                            year = int(w_clean)
                            break

            # 2. Skrapa Färg
            color = "Okänd"
            color_node = soup.find(string=lambda t: t and "Färg" in t)
            if color_node and color_node.parent:
                text = color_node.parent.parent.get_text() if color_node.parent.parent else color_node.parent.get_text()
                for c in ["Svart", "Vit", "Grå", "Silver", "Röd", "Blå", "Grön", "Gul", "Brun", "Mörkgrå"]:
                    if c.lower() in text.lower():
                        color = c
                        break

            # 3. Skrapa Drivmedel
            fuel_type = "Bensin/Diesel"
            if "diesel" in page_text.lower():
                fuel_type = "Diesel"
            elif "elhybrid" in page_text.lower() or "laddhybrid" in page_text.lower():
                fuel_type = "Hybrid"
            elif "ren el" in page_text.lower():
                fuel_type = "El"
            elif "bensin" in page_text.lower():
                fuel_type = "Bensin"

            # 4. Skrapa Växellåda
            gearbox = "Manuell"
            if "automat" in page_text.lower() or "aut" in page_text.lower():
                gearbox = "Automat"

            # 5. Skrapa Senaste Besiktningsmiltal (Mätarställning)
            inspected_mileage = "Ej angivet"
            # Sök efter mönster som "Mätarställning: 14 320 mil" eller "143 200 km"
            mileage_match = re.search(r'(?:mätarställning|besiktning|miltal)[\s\:\-]*([\d\s]{3,8})\s*(mil|km)', page_text, re.IGNORECASE)
            
            if mileage_match:
                raw_val = mileage_match.group(1).replace(" ", "").strip()
                unit = mileage_match.group(2).lower()
                if raw_val.isdigit():
                    num = int(raw_val)
                    if unit == "km":
                        num = round(num / 10)
                    inspected_mileage = f"{num:,} mil".replace(",", " ")
            else:
                # Sök alternativt efter siffror följda av "mil" i tabeller
                mil_matches = re.findall(r'(\d{1,3}(?:\s?\d{3})*)\s*mil', page_text, re.IGNORECASE)
                if mil_matches:
                    inspected_mileage = f"{mil_matches[0].strip()} mil"

            print(f"✅ [LIVE MATCH] {clean_reg} -> {make} {model} ({year}), Besiktningsmiltal: {inspected_mileage}")

            return Vehicle(
                reg_number=clean_reg,
                make=make,
                model=model,
                year=year,
                engine=f"{make} {model}",
                color=color,
                fuel_type=fuel_type,
                gearbox=gearbox,
                inspected_mileage=inspected_mileage,
                vin=f"VIN-{clean_reg}"
            )

    except Exception as e:
        print(f"⚠️ Skrapning misslyckades: {e}")

    return Vehicle(
        reg_number=clean_reg,
        make="Bil",
        model=f"Reg: {clean_reg}",
        year=2018,
        engine="Standard",
        color="Okänd",
        fuel_type="Okänd",
        gearbox="Okänd",
        inspected_mileage="Ej angivet",
        vin=f"VIN-{clean_reg}"
    )