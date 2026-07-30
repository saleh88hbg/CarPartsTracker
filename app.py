import streamlit as st
from database import init_db, engine, Vehicle
from car_fetcher import fetch_vehicle_by_reg
from service_advisor import analyze_service_needs
from price_scraper import search_live_prices
from sqlmodel import Session, select

st.set_page_config(
    page_title="CarParts Tracker & Service Advisor",
    page_icon="🚗",
    layout="wide"
)

init_db()

st.title("🚗 CarParts Tracker & Service Advisor")
st.caption("Mata in bilens registreringsnummer och miltal för att få expertrekommendationer och jämföra live-priser.")

st.divider()

# --- SÖKFORMULÄR ---
col1, col2, col3 = st.columns([2, 2, 1])

with col1:
    reg_num_input = st.text_input("Registreringsnummer", placeholder="t.ex. LLE072").strip().upper()

with col2:
    mileage_input = st.number_input("Nuvarande miltal (i mil)", min_value=0, value=15000, step=500)

with col3:
    st.write("##")
    search_button = st.button("🔍 Sök & Analysera", type="primary", use_container_width=True)

# --- SÖKLOGIK ---
if search_button and reg_num_input:
    mileage_km = int(mileage_input) * 10

    with st.spinner("Hämtar fordonsdata live från nätet och söker priser..."):
        vehicle = fetch_vehicle_by_reg(reg_num_input)

        if not vehicle:
            st.error(f"Kunde inte hämta fordonsdata för **{reg_num_input}**.")
        else:
            with Session(engine) as session:
                session.merge(vehicle)
                session.commit()

            # --- FORDONSKORT ---
            st.success(f"### 🚘 {vehicle.make} {vehicle.model} ({vehicle.year})")
            
            # Rad 1: Regnr, Inmatat miltal, Besiktningsmiltal
            info_col1, info_col2, info_col3 = st.columns(3)
            info_col1.metric("Reg-nummer", vehicle.reg_number)
            info_col2.metric("Inmatat Miltal", f"{mileage_input:,} mil".replace(",", " "))
            info_col3.metric("📋 Besiktningsmiltal", getattr(vehicle, "inspected_mileage", "Ej angivet"))

            # Rad 2: Färg, Drivmedel, Växellåda
            info_col4, info_col5, info_col6 = st.columns(3)
            info_col4.metric("Färg", getattr(vehicle, "color", "Okänd"))
            info_col5.metric("Drivmedel", getattr(vehicle, "fuel_type", "Okänd"))
            info_col6.metric("Växellåda", getattr(vehicle, "gearbox", "Okänd"))

            st.divider()
            st.subheader("💡 Expertrekommenderade Servicepaket & Live-Priser")

            service_items = analyze_service_needs(mileage_km, vehicle.year, vehicle.engine)

            for idx, item in enumerate(service_items, 1):
                if item.urgency == "AKUT":
                    badge = "🚨 AKUT BEHOV"
                elif item.urgency == "REKOMMENDERAS":
                    badge = "⚠️ REKOMMENDERAS"
                else:
                    badge = "ℹ️ KOMMANDE"

                with st.expander(f"{badge} — {item.name}", expanded=True):
                    st.write(f"**Kategori:** {item.category}")
                    st.write(f"**Beskrivning:** {item.description}")
                    st.markdown("##### 🛒 Skarpa Live-Priser hos Trodo")

                    main_keyword = item.search_keywords[0]
                    prices = search_live_prices(main_keyword)

                    if prices:
                        for p in prices:
                            total_price = p["price_sek"] + p["shipping_cost_sek"]
                            stock_str = "🟢 I lager" if p["in_stock"] else "🔴 Ej i lager"
                            
                            p_col1, p_col2, p_col3, p_col4 = st.columns([3, 2, 2, 2])
                            p_col1.write(f"**{p['store_name']}** — {p.get('title', main_keyword)}")
                            p_col2.write(f"Pris: **{p['price_sek']:.0f} kr** (+ {p['shipping_cost_sek']:.0f} kr frakt)")
                            p_col3.write(f"Totalt: **{total_price:.0f} kr** ({stock_str})")
                            p_col4.markdown(f"[👉 Gå till produkt/sökning]({p['url']})")

elif search_button and not reg_num_input:
    st.warning("Vänligen mata in ett registreringsnummer först.")