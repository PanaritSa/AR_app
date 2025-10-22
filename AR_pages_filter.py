# AR_pages_filter.py
import pandas as pd
import streamlit as st
from AR_pagination import paginate_results

def render_filter(df):
    st.subheader("🔍 Search by Filter + Map + Tags")
    col1, col2 = st.columns(2)
    with col1:
        min_price = st.number_input("Min Price", 0)
    with col2:
        max_price = st.number_input("Max Price", 100000000)

    location_input = st.selectbox("Location", ["", "Sukhumvit", "Silom", "Sathorn", "Ari", "Rama 9"])

    all_facility_tags = sorted(set(tag.strip() for tags in df["facilities"].dropna().str.split(",") for tag in tags))
    selected_facility_tags = st.multiselect("🏷 Tags (Facilities)", options=all_facility_tags)

    nearby_tag_options = [
        "Hospital", "School", "Shopping Mall", "Park", "Public Transport",
        "University", "Market", "Office Building", "Restaurant Hub", "Cultural Site"
    ]
    selected_nearby_tags = st.multiselect("📍 Nearby Places", options=nearby_tag_options)

    st.map(df[["latitude", "longitude"]].dropna(), zoom=6)

    if st.button("Search", key="filter_button"):
        results = df[
            (df["price"].astype(float) >= min_price) &
            (df["price"].astype(float) <= max_price)
        ]

        if location_input:
            results = results[results["address"].str.contains(location_input, case=False, na=False)]

        if selected_facility_tags:
            results = results[
                results["facilities"].apply(
                    lambda x: any(tag.strip() in x.split(",") for tag in selected_facility_tags) if pd.notna(x) else False
                )
            ]

        if selected_nearby_tags:
            results = results[
                results["magnet"].apply(
                    lambda x: any(tag.strip() in x.split(",") for tag in selected_nearby_tags) if pd.notna(x) else False
                )
            ]

        st.session_state.search_results = results.to_dict(orient="records")
        st.session_state.previous_page = "Filter"
        st.rerun()

    if st.session_state.get("search_results"):
        results_df = pd.DataFrame(st.session_state.search_results)
        st.write(f"### Found {len(results_df)} results:")
        paginated = paginate_results(results_df, page_key="filter_page")
        for i, (_, row) in enumerate(paginated.iterrows()):
            st.image(row["image_path"], caption=row["style"], width=300)
            if st.button(f"View Details: {row['address']}", key=f"filter_result_{i}"):
                st.session_state.selected_house = row.to_dict()
                st.session_state.return_page = "Filter"
                st.rerun()

    if st.button("Clear Search and Return to Home", key="clear_filter"):
        st.session_state.search_results = None
        st.session_state.page = "Home"
        st.rerun()
