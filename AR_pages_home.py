# AR_pages_home.py
import streamlit as st
from AR_map import folium_click, within_radius
from AR_pagination import paginate_results

def render_home(df):
    st.subheader("🗺 Click Anywhere to Find Houses Within 3 KM")

    map_data = folium_click(df, width=700, height=500)
    if map_data and map_data.get("last_clicked"):
        clicked_lat = map_data["last_clicked"]["lat"]
        clicked_lon = map_data["last_clicked"]["lng"]
        clicked_point = (clicked_lat, clicked_lon)

        st.session_state["map_click_location"] = clicked_point
        st.success(f"📍 Clicked at: {clicked_point}")

        nearby_df = df[df.apply(lambda row: within_radius(row, clicked_point), axis=1)]

        st.markdown("### 🏡 Houses Within 3 KM")
        if not nearby_df.empty:
            paginated = paginate_results(nearby_df, page_key="folium_radius")
            for i, (_, row) in enumerate(paginated.iterrows()):
                st.image(row["image_path"], caption=row["style"], width=300)
                if st.button(f"View Details: {row['address']}", key=f"folium_result_{i}"):
                    st.session_state.selected_house = row.to_dict()
                    st.session_state.return_page = "Home"
                    st.rerun()
        else:
            st.info("No houses found within 3 KM.")
