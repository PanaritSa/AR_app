# AR_pages_style.py
import pandas as pd
import streamlit as st
from AR_pagination import paginate_results

STYLE_ICONS = {
    "ML-AR-COLONIAL": "🏛️",
    "ML-AR-Chicago School": "🏙️",
    "ML-AR-Classic": "🕍",
    "ML-AR-MEDITERRANEAN": "🌅",
    "ML-AR-MID CENTURY": "📻",
    "ML-AR-Modern": "🏢",
    "ML-AR-Modern Minimal": "📐",
    "ML-AR-Oriental": "🏯",
    "ML-AR-SCANDINAVIAN": "❄️",
    "ML-AR-THAI": "🛕",
    "ML-AR-TRANSITIONAL": "🔄",
    "ML-AR-TUDOR HOUSE": "🏡",
    "ML-AR-VICTORIAN": "👑",
}

def render_style(df):
    st.subheader("🎨 เลือกสไตล์บ้านที่คุณสนใจ")

    available_styles = sorted(df["style"].unique())
    cols = st.columns(4)
    for i, style in enumerate(available_styles):
        icon = STYLE_ICONS.get(style, "🏠")
        readable_name = style.replace("ML-AR-", "").title()
        with cols[i % 4]:
            if st.button(f"{icon}\n{readable_name}", key=f"style_{style}"):
                st.session_state.style_results = df[df["style"] == style].to_dict(orient="records")
                st.session_state.page = "Style"
                st.rerun()

    if st.session_state.get("style_results"):
        style_df = pd.DataFrame(st.session_state.style_results)
        paginated = paginate_results(style_df, page_key="style_page")
        for i, (_, row) in enumerate(paginated.iterrows()):
            st.image(row["image_path"], caption=row["style"], width=300)
            if st.button(f"View Details: {row['address']}", key=f"style_result_{i}"):
                st.session_state.selected_house = row.to_dict()
                st.session_state.return_page = "Style"
                st.rerun()
