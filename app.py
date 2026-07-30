import streamlit as st
from database import init_db, engine, Vehicle
from car_fetcher import fetch_vehicle_by_reg
from service_advisor import analyze_service_needs
from price_scraper import search_live_prices
from sqlmodel import Session, select

# 1. Konfigurera Streamlit-sidan
st.set_page_config(
    page_title="CarParts Tracker & Service Advisor",
    page_icon="🚗",
    layout="wide"
)

# Initiera databasen
init_db()

# --- RUBRIK & INTRO ---
st.title("🚗 CarParts Tracker & Service Advisor")
st.caption("Mata in bilens registreringsnummer och miltal för att få expertrekommendationer och jämföra live-priser på reservdelar.")

st.divider()

# --- SÖKFORMULÄR ---
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    reg_num_input = st.text_input("Registreringsnummer", placeholder="t.ex. ABC123").strip().upper()

with col2:
    mileage_input = st.number_input("Nuvarande miltal (i mil)", min_value=0, value=12500, step=500)

with col3:
    st.write("##") # Avståndsskapare för knappen
    search_button = st.button("🔍 Sök & Analysera", type="primary", use_container_width=True)

# --- SÖKLOGIK & VISNING ---
if search_button and reg_num_input:
    mileage_km = int(mileage_input) * 10

    with st.spinner("Hämtar fordonsdata och söker live-priser..."):
        # 1. Hämta/Cacha fordon i SQLite
        with Session(engine) as session:
            statement = select(Vehicle).where(Vehicle.reg_number == reg_num_input)
            vehicle = session.exec(statement).first()

            if not vehicle:
                vehicle = fetch_vehicle_by_reg(reg_num_input)
                if vehicle:
                    session.add(vehicle)
                    session.commit()
                    session.refresh(vehicle)

        if not vehicle:
            st.error(f"Kunde inte hitta information för registreringsnummer **{reg_num_input}**.")
        else:
            # Display Vehicle Info Card
            st.success(f"### 🚘 {vehicle.make} {vehicle.model} ({vehicle.year})")
            
            info_col1, info_col2, info_col3 = st.columns(3)
            info_col1.metric("Motor", vehicle.engine)
            info_col2.metric("Miltal", f"{mileage_input:,} mil".replace(",", " "))
            info_col3.metric("VIN / Chassinr", vehicle.vin or "Ej tillgängligt")

            st.divider()
            st.subheader("💡 Expertrekommenderade Servicepaket & Live-Priser")

            # 2. Analysera servicebehov
            service_items = analyze_service_needs(mileage_km, vehicle.year, vehicle.engine)

            for idx, item in enumerate(service_items, 1):
                # Färgkodning baserat på hur akut servicen är
                if item.urgency == "AKUT":
                    badge = "🚨 AKUT BEHOV"
                elif item.urgency == "REKOMMENDERAS":
                    badge = "⚠️ REKOMMENDERAS"
                else:
                    badge = "ℹ️ KOMMANDE"

                with st.expander(f"{badge} — {item.name}", expanded=True):
                    st.write(f"**Kategori:** {item.category}")
                    st.write(f"**Beskrivning:** {item.description}")
                    
                    st.markdown("##### 🛒 Skarpa Live-Priser i Butik")

                    main_keyword = item.search_keywords[0]
                    prices = search_live_prices(main_keyword)

                    if prices:
                        for p in prices:
                            total_price = p["price_sek"] + p["shipping_cost_sek"]
                            stock_str = "🟢 I lager" if p["in_stock"] else "🔴 Ej i lager"
                            
                            p_col1, p_col2, p_col3, p_col4 = st.columns([3, 2, 2, 2])
                            
                            p_col1.write(f"**{p['store_name']}** — {p.get('title', main_keyword)}")
                            p_col2.write(f"Produkt: **{p['price_sek']:.0f} kr** (+ {p['shipping_cost_sek']:.0f} kr frakt)")
                            p_col3.write(f"Totalt: **{total_price:.0f} kr** ({stock_str})")
                            p_col4.markdown(f"[👉 Gå till butik]({p['url']})")
                    else:
                        st.info("Hittade inga live-priser just nu.")

elif search_button and not reg_num_input:
    st.warning("Vänligen mata in ett registreringsnummer först.")