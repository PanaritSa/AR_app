# AR_pages_favorites.py
import streamlit as st
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def render_favorites(df, feature_list, filenames):
    st.title("🌟 บ้านที่คุณถูกใจ (Favorites)")

    if st.session_state.favorites:
        st.write(f"❤️ คุณมีบ้านถูกใจทั้งหมด {len(st.session_state.favorites)} หลัง")

        for i, house in enumerate(st.session_state.favorites):
            st.image(house["image_path"], width=300)
            st.write(f"**Address:** {house['address']}")
            st.write(f"**Price:** {house['price']} THB")
            st.write(f"**Style:** {house['style']}")
            st.write(f"**Facilities:** {house['facilities']}")
            st.write(f"**Nearby:** {house['magnet']}")
            st.write(f"**Area:** {house['area_size']} sqm")

            if "lifestyle_tags" in house and house["lifestyle_tags"]:
                st.write(f"**Lifestyle Tags:** {' '.join(house['lifestyle_tags'])}")
            else:
                st.write("**Lifestyle Tags:** -")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("🗑️ ลบออกจาก Favorites", key=f"remove_fav_{i}"):
                    del st.session_state.favorites[i]
                    st.rerun()
            with col2:
                if st.button("🏡 ดูบ้านที่คล้ายกัน", key=f"similar_fav_{i}"):
                    if house["image_path"] in filenames:
                        base_idx = filenames.index(house["image_path"])
                        base_vec = feature_list[base_idx].reshape(1, -1)
                        sims = cosine_similarity(feature_list, base_vec).flatten()
                        top_idx = np.argsort(sims)[-6:-1][::-1]
                        paths = [filenames[k] for k in top_idx]
                        sim_df = df[df["image_path"].isin(paths)].copy()
                        sim_df["similarity"] = sim_df["image_path"].apply(
                            lambda p: sims[filenames.index(p)] if p in filenames else 0
                        )
                        sim_df = sim_df.sort_values(by="similarity", ascending=False)
                        st.markdown("### 🔁 บ้านที่คล้ายกัน")
                        for j, (_, sim_row) in enumerate(sim_df.iterrows()):
                            st.image(sim_row["image_path"], width=250, caption=f"{sim_row['style']} ({sim_row['similarity']:.2f})")
                            st.caption(f"{sim_row['address']} — {sim_row['price']} THB")
                            if st.button(f"ดูรายละเอียด: {sim_row['address']}", key=f"similar_detail_{i}_{j}"):
                                st.session_state.selected_house = sim_row.to_dict()
                                st.session_state.return_page = "Favorites"
                                st.rerun()

            if st.button("🔎 View Details", key=f"fav_detail_{i}"):
                st.session_state.selected_house = house
                st.session_state.return_page = "Favorites"
                st.rerun()
    else:
        st.info("คุณยังไม่มีบ้านใน Favorites เลย ลองไปกด ❤️ ในหน้า Lifestyle ดูสิ!")
