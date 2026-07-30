import requests
from typing import Optional
from database import Vehicle

def fetch_vehicle_by_reg(reg_number: str) -> Optional[Vehicle]:
    """
    Hämtar fordonsdata baserat på registreringsnummer.
    Här kopplar vi på API-anrop eller scraping mot bilkällor.
    """
    clean_reg = reg_number.strip().upper().replace(" ", "").replace("-", "")
    
    if len(clean_reg) != 6:
        print(f"❌ Felaktigt registreringsnummer: {reg_number}")
        return None

    print(f"🔍 Söker fordonsdata för {clean_reg}...")

    # TODO: Här kopplar vi på riktiga API-anrop eller scraping.
    # För att testa flödet returnerar vi tills vidare strukturerad data:
    
    # Exempellogik för testning:
    fake_database = {
        "ABC123": {"make": "Volvo", "model": "V60", "year": 2019, "engine": "D4 190hk (D4204T14)", "vin": "YV1ZW0821K1000000"},
        "XYZ987": {"make": "Volkswagen", "model": "Passat", "year": 2017, "engine": "2.0 TDI 150hk", "vin": "WVWZZZ3CZHE000000"},
    }

    if clean_reg in fake_database:
        data = fake_database[clean_reg]
        return Vehicle(
            reg_number=clean_reg,
            make=data["make"],
            model=data["model"],
            year=data["year"],
            engine=data["engine"],
            vin=data["vin"]
        )
    else:
        # Om det är ett okänt reg-nr skapar vi en generisk bil som fallback under utveckling
        return Vehicle(
            reg_number=clean_reg,
            make="Okänt Märke",
            model="Okänd Modell",
            year=2020,
            engine="Okänd Motor",
            vin=None
        )