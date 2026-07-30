def main():
    print("=== RESERVDELSKOLLEN ===")
    reg_num = input("Mata in reg-nr (t.ex. ABC123): ").strip().upper()
    print(f"\nSöker bildata för: {reg_num}...")
    # Här bygger vi vidare på söklogiken!

if __name__ == "__main__":
    main()

from database import init_db, engine, Vehicle, Part, PriceHistory
from sqlmodel import Session, select

def main():
    # Skapa databasen och tabellerna om de saknas
    init_db()
    print("✅ Databasen 'carparts.db' är täckningsredo och initierad!")

    reg_num = input("\nMata in reg-nr (t.ex. ABC123): ").strip().upper()

    with Session(engine) as session:
        # Kolla om bilen redan finns i databasen (caching)
        statement = select(Vehicle).where(Vehicle.reg_number == reg_num)
        vehicle = session.exec(statement).first()

        if not vehicle:
            print(f"Söker nytt fordon... (Sparar till databasen)")
            # Simulerad hämtning från externt API/Scraper
            vehicle = Vehicle(
                reg_number=reg_num,
                make="Volvo",
                model="V60",
                year=2019,
                engine="D4 190hk"
            )
            session.add(vehicle)
            session.commit()
            session.refresh(vehicle)
            print(f"💾 Sparade ny bil i databasen: {vehicle.make} {vehicle.model}")
        else:
            print(f"⚡ Hittade bilen direkt i databasen (cache): {vehicle.make} {vehicle.model}")

if __name__ == "__main__":
    main()