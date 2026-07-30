from typing import List, Dict
from pydantic import BaseModel

class ServiceItem(BaseModel):
    name: str                   # t.ex. "Motorolja + Oljefilter"
    interval_km: int            # t.ex. 15000
    interval_years: int         # t.ex. 1
    urgency: str                # "AKUT", "REKOMMENDERAS", "KOMMANDE"
    category: str               # "Liten service", "Stor service", "Drivlina"
    search_keywords: List[str]  # Sökord för scrapers/delar (t.ex. ["Oljefilter", "5W-30"])
    description: str

def analyze_service_needs(mileage_km: int, vehicle_year: int, engine_type: str) -> List[ServiceItem]:
    """
    Analyserar bilens miltal och ålder och returnerar rekommenderade serviceåtgärder.
    """
    current_year = 2026  # Nuvarande år
    age_years = current_year - vehicle_year
    recommendations = []

    # 1. Liten Service (Basunderhåll: Olja & Filter)
    recommendations.append(ServiceItem(
        name="Liten Service (Motorolja & Oljefilter)",
        interval_km=15000,
        interval_years=1,
        urgency="REKOMMENDERAS",
        category="Liten service",
        search_keywords=["Oljefilter", "Motorolja 5W-30"],
        description="Standard oljebyte för att förhindra slitage på motorns inre komponenter."
    ))

    # 2. Stor Service (Tändstift / Glödstift + Alla filter)
    if mileage_km >= 60000 or age_years >= 4:
        recommendations.append(ServiceItem(
            name="Stor Service (Luft-, Kupé- & Bränslefilter)",
            interval_km=60000,
            interval_years=4,
            urgency="AKUT" if mileage_km % 60000 < 5000 else "REKOMMENDERAS",
            category="Stor service",
            search_keywords=["Luftfilter", "Kupéfilter", "Bränslefilter"],
            description="Bytes av luft- och kupéfilter samt tändstift/bränslefilter för optimal förbränning och ren kupéluft."
        ))

    # 3. Växellådsolja (Automatlåda / DSG / Torque Converter)
    if "auto" in engine_type.lower() or "dsg" in engine_type.lower() or mileage_km >= 80000:
        recommendations.append(ServiceItem(
            name="Spolning & Byte av Automatlådeolja",
            interval_km=80000,
            interval_years=6,
            urgency="REKOMMENDERAS" if mileage_km >= 80000 else "KOMMANDE",
            category="Drivlina",
            search_keywords=["Växellådsolja Automat", "Hydraulfilter"],
            description="Många tillverkare hävdar 'lifetime fluid', men oljan bryts ner. Byte vid 8 000 - 10 000 mil förhindrar dyra växellådsreparationer."
        ))

    # 4. Kamrem vs Kamkedja
    if "d4" in engine_type.lower() or mileage_km >= 120000 or age_years >= 8:
        recommendations.append(ServiceItem(
            name="Kamremsbyte inkl. Vattenpump & Spännare",
            interval_km=150000,
            interval_years=10,
            urgency="AKUT" if (mileage_km >= 140000 or age_years >= 9) else "REKOMMENDERAS",
            category="Kamrem / Drivrem",
            search_keywords=["Kamremsats", "Vattenpump"],
            description="Kritiskt underhåll! Om kamremmen brister kan det leda till totalt motorhaveri."
        ))

    return recommendations