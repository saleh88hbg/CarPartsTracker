from database import init_db, engine, Vehicle
from car_fetcher import fetch_vehicle_by_reg
from service_advisor import analyze_service_needs
from price_scraper import search_live_prices
from sqlmodel import Session, select

def main():
    init_db()
    print("==================================================")
    print("      CAR PARTS TRACKER & SERVICE ADVISOR         ")
    print("==================================================\n")

    reg_num = input("Mata in reg-nr (t.ex. ABC123): ").strip().upper()
    try:
        mileage_input = input("Mata in nuvarande miltal (i mil, t.ex. 12500): ").strip()
        mileage = int(mileage_input) * 10
    except ValueError:
        mileage = 120000

    with Session(engine) as session:
        statement = select(Vehicle).where(Vehicle.reg_number == reg_num)
        vehicle = session.exec(statement).first()

        if not vehicle:
            vehicle = fetch_vehicle_by_reg(reg_num)
            if vehicle:
                session.add(vehicle)
                session.commit()
                session.refresh(vehicle)

        if not vehicle:
            print("Kunde inte hitta fordonet.")
            return

        print(f"\n🚗 FORDON: {vehicle.make} {vehicle.model} ({vehicle.year}) - {vehicle.engine}")
        print(f"📏 MILTAL: {mileage // 10} mil ({mileage} km)")

        print("\n--------------------------------------------------")
        print("💡 EXPERTREKOMMENDERADE SERVICEPAKET")
        print("--------------------------------------------------")
        service_items = analyze_service_needs(mileage, vehicle.year, vehicle.engine)

        for idx, item in enumerate(service_items, 1):
            urgency_icon = "🚨" if item.urgency == "AKUT" else ("⚠️" if item.urgency == "REKOMMENDERAS" else "ℹ️")
            print(f"\n{idx}. {urgency_icon} [{item.category.upper()}] {item.name}")
            print(f"   Beskrivning: {item.description}")
            
            main_keyword = item.search_keywords[0]
            prices = search_live_prices(main_keyword)

            print("   --- Skarpa Live-Priser ---")
            for p in prices:
                total = p["price_sek"] + p["shipping_cost_sek"]
                stock_status = "I lager" if p["in_stock"] else "Ej i lager"
                title_str = f" ({p.get('title')})" if 'title' in p else ""
                print(f"   • {p['store_name']}{title_str}: {p['price_sek']:.0f} kr (+ {p['shipping_cost_sek']:.0f} kr frakt) = Totalt: {total:.0f} kr [{stock_status}]")
                print(f"     🔗 Länk: {p['url']}")

if __name__ == "__main__":
    main()