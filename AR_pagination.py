# AR_pagination.py
import streamlit as st
from AR_constants import PAGE_SIZE_OPTIONS, DEFAULT_PAGE_SIZE

def paginate_results(df, page_key: str):
    size_key = f"{page_key}_size"
    page_number_key = page_key

    if size_key not in st.session_state:
        st.session_state[size_key] = DEFAULT_PAGE_SIZE
    if page_number_key not in st.session_state:
        st.session_state[page_number_key] = 1

    page_size = st.selectbox(
        "Houses per page:",
        PAGE_SIZE_OPTIONS,
        index=PAGE_SIZE_OPTIONS.index(st.session_state[size_key]),
        key=f"{size_key}_select"
    )
    if page_size != st.session_state[size_key]:
        st.session_state[size_key] = page_size
        st.session_state[page_number_key] = 1
        st.rerun()

    total_items = len(df)
    current_page = st.session_state[page_number_key]
    total_pages = (total_items - 1) // page_size + 1
    current_page = min(current_page, total_pages)
    start_idx = (current_page - 1) * page_size
    end_idx = min(start_idx + page_size, total_items)

    st.markdown(f"**Showing {start_idx + 1}–{end_idx} of {total_items} houses**")
    col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])
    with col1:
        if st.button("🏠 First", key=f"{page_key}_first"):
            st.session_state[page_number_key] = 1
            st.rerun()
    with col2:
        if st.button("⬅️ Prev", key=f"{page_key}_prev") and current_page > 1:
            st.session_state[page_number_key] -= 1
            st.rerun()
    with col3:
        st.markdown(f"<div style='text-align: center; font-weight: bold;'>Page {current_page} of {total_pages}</div>", unsafe_allow_html=True)
    with col4:
        if st.button("➡️ Next", key=f"{page_key}_next") and current_page < total_pages:
            st.session_state[page_number_key] += 1
            st.rerun()
    with col5:
        if st.button("⏭️ Last", key=f"{page_key}_last"):
            st.session_state[page_number_key] = total_pages
            st.rerun()
    return df.iloc[start_idx:end_idx]
