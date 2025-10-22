# AR_ui.py
import pandas as pd
import streamlit as st
import pydeck as pdk
import matplotlib.pyplot as plt
from sklearn.metrics.pairwise import cosine_similarity
from AR_constants import MAPBOX_STYLE
from AR_pagination import paginate_results

def home_button():
    if st.button("🏠 Go to Home"):
        st.session_state.page = "Home"
        st.session_state.selected_house = None
        st.rerun()

def menu_bar():
    st.markdown("### 🧭 เมนูหลัก")
    menu_items = [
        {"name": "Home", "icon": "🏠"},
        {"name": "My Lifestyle", "icon": "💖"},
        {"name": "Favorites", "icon": "🌟"},
        {"name": "Filter", "icon": "🔍"},
        {"name": "Classify", "icon": "📷"},
        {"name": "Style", "icon": "🎨"},
    ]
    cols = st.columns(len(menu_items))
    for i, item in enumerate(menu_items):
        with cols[i]:
            if st.button(f"{item['icon']}", key=f"menu_button_{item['name']}"):
                st.session_state.previous_page = st.session_state.page
                st.session_state.page = item["name"]
                st.session_state.search_results = None
                st.session_state.style_results = None
                st.session_state.classify_results = {}
                st.session_state.selected_house = None
                st.rerun()
            st.markdown(f"<div style='text-align: center;'>{item['name']}</div>", unsafe_allow_html=True)

def show_house_details(row, df, feature_list, filenames, get_recommendations_fn):
    st.image(row["image_path"], caption=row["style"], width=500)
    st.write(f"**Address:** {row['address']}")
    st.write(f"**Price:** {row['price']} THB")
    st.write(f"**Bedrooms:** {row['bedrooms']}, **Bathrooms:** {row['bathrooms']}")
    st.write(f"**Area:** {row['area_size']} sqm")
    st.write(f"**Facilities:** {row['facilities']}")
    st.write(f"**Nearby Places:** {row['magnet']}")

    with st.expander("💸 Estimated Mortgage Calculator"):
        property_price = float(row["price"])
        downpayment_percent = st.slider("Downpayment (%)", 0, 50, 10, step=1)
        interest_rate = st.number_input("Interest Rate (% per year)", min_value=0.0, max_value=15.0, value=5.0, step=0.1)
        loan_years = st.number_input("Loan Tenure (years)", min_value=1, max_value=40, value=30)

        downpayment = property_price * downpayment_percent / 100
        loan_amount = property_price - downpayment
        monthly_interest = interest_rate / 100 / 12
        months = loan_years * 12

        if loan_amount > 0 and monthly_interest > 0:
            monthly_payment = loan_amount * monthly_interest * (1 + monthly_interest) ** months / ((1 + monthly_interest) ** months - 1)
            total_payment = monthly_payment * months
            total_interest = total_payment - loan_amount
            principal_pct = loan_amount / total_payment * 100
            interest_pct = total_interest / total_payment * 100

            st.markdown(f"### 💰 Est. Monthly Payment: **฿ {monthly_payment:,.0f} / mo**")
            st.progress(int(principal_pct), text=f"📘 Principal: ฿ {loan_amount:,.0f} ({principal_pct:.0f}%)")
            st.progress(int(interest_pct), text=f"💸 Interest: ฿ {total_interest:,.0f} ({interest_pct:.0f}%)")

            st.markdown("---")
            st.markdown(f"#### 🧾 Upfront Cost")
            st.write(f"🔹 Downpayment: **฿ {downpayment:,.0f}** ({downpayment_percent}%)")
            st.write(f"🔹 Loan Amount: **฿ {loan_amount:,.0f}** ({100 - downpayment_percent}%)")

            schedule = []
            balance = loan_amount
            for year in range(1, loan_years + 1):
                principal_year = 0
                interest_year = 0
                for _ in range(12):
                    interest = balance * monthly_interest
                    principal = monthly_payment - interest
                    balance -= principal
                    principal_year += principal
                    interest_year += interest
                schedule.append({"Year": year, "Principal": max(principal_year, 0), "Interest": max(interest_year, 0)})
            schedule_df = pd.DataFrame(schedule)

            st.markdown("#### 📊 Repayment Breakdown by Year")
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.bar(schedule_df["Year"], schedule_df["Principal"], label="Principal", alpha=0.7)
            ax.bar(schedule_df["Year"], schedule_df["Interest"], bottom=schedule_df["Principal"], label="Interest", alpha=0.7)
            ax.set_xlabel("Year"); ax.set_ylabel("Amount (THB)")
            ax.set_title("Annual Repayment Breakdown"); ax.legend()
            st.pyplot(fig)
        else:
            st.warning("กรุณากรอกข้อมูลให้ครบและถูกต้องเพื่อคำนวณสินเชื่อ")

    lat, lon = row.get("latitude"), row.get("longitude")
    if lat and lon:
        icon_data = [{
            "position": [lon, lat],
            "icon": {
                "url": "https://cdn-icons-png.flaticon.com/512/684/684908.png",
                "width": 128, "height": 128, "anchorY": 128
            }
        }]
        st.pydeck_chart(pdk.Deck(
            map_style=MAPBOX_STYLE,
            initial_view_state=pdk.ViewState(latitude=lat, longitude=lon, zoom=15),
            layers=[
                pdk.Layer("IconLayer", data=icon_data, get_icon="icon", get_position="position", size_scale=15, pickable=True)
            ]
        ))

    st.subheader("🏘️ Similar Houses You May Like (Ranked)")
    similar_paths = get_recommendations_fn(row["image_path"])
    sim_df = df[df["image_path"].isin(similar_paths)].copy()

    def sim_score(path):
        if path in filenames and row["image_path"] in filenames:
            from_idx = filenames.index(path)
            to_idx = filenames.index(row["image_path"])
            return cosine_similarity(
                feature_list[from_idx].reshape(1, -1),
                feature_list[to_idx].reshape(1, -1)
            )[0][0]
        return 0
    sim_df["similarity"] = sim_df["image_path"].apply(sim_score)
    sim_df = sim_df.sort_values(by="similarity", ascending=False)

    for i, (_, sim_row) in enumerate(sim_df.iterrows()):
        st.image(sim_row["image_path"], width=250, caption=f"{sim_row['style']} ({sim_row['similarity']:.2f})")
        st.caption(f"{sim_row['address']} — {sim_row['price']} THB")
        if st.button(f"View Details: {sim_row['address']}", key=f"similar_result_{i}"):
            st.session_state.selected_house = sim_row.to_dict()
            st.session_state.return_page = st.session_state.page
            st.rerun()

    if st.button("🔙 Back"):
        st.session_state.page = st.session_state.return_page
        st.session_state.selected_house = None
        st.rerun()
