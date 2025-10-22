# AR_app.py
import streamlit as st

from AR_constants import HERO_IMAGE, IMAGE_SIZE
from AR_resources import get_resources
from AR_lifestyle import extract_lifestyle_tags, match_score
from AR_ui import menu_bar, home_button, show_house_details
from AR_features import get_recommendations
from AR_pages_home import render_home
from AR_pages_classify import render_classify
from AR_pages_filter import render_filter
from AR_pages_style import render_style
from AR_pages_favorites import render_favorites

st.set_page_config(page_title="House Finder", layout="wide")

R = get_resources()
df = R["df"]
model_classification = R["model_classification"]
base_model = R["base_model"]
pooling_layer = R["pooling_layer"]
feature_list = R["feature_list"]
filenames = R["filenames"]

if "lifestyle_tags" not in df.columns:
    df["lifestyle_tags"] = df.apply(lambda row: extract_lifestyle_tags(row.get("magnet"), row.get("facilities")), axis=1)

st.image(HERO_IMAGE, width=600)

for key, default in {
    "page": "Home",
    "selected_house": None,
    "search_results": None,
    "previous_page": "Home",
    "return_page": "Home",
    "classify_results": {},
    "style_results": None,
    "favorites": [],
    "swipe_index": 0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

menu_bar()

if st.session_state.page != st.session_state.previous_page:
    st.session_state.previous_page = st.session_state.page
    st.session_state.search_results = None
    st.session_state.style_results = None
    st.session_state.classify_results = {}
    st.session_state.selected_house = None
    st.rerun()

if st.session_state.selected_house:
    home_button()
    show_house_details(
        st.session_state.selected_house,
        df=df,
        feature_list=feature_list,
        filenames=filenames,
        get_recommendations_fn=lambda p: get_recommendations(p, filenames, feature_list, topk=5)
    )

elif st.session_state.page == "Home":
    render_home(df)

elif st.session_state.page == "Classify":
    home_button()
    render_classify(df, model_classification, base_model, pooling_layer, feature_list, filenames)

elif st.session_state.page == "Filter":
    home_button()
    render_filter(df)

elif st.session_state.page == "Style":
    home_button()
    render_style(df)

elif st.session_state.page == "Favorites":
    home_button()
    render_favorites(df, feature_list, filenames)

elif st.session_state.page == "My Lifestyle":
    home_button()
    st.subheader("💖 ค้นหาบ้านที่ตรงกับไลฟ์สไตล์ของคุณ")

    st.markdown("#### 🧠 คุณคิดว่าคุณเป็นคนแบบไหน?")
    personality = st.multiselect("เลือกได้มากกว่า 1 ข้อ", ["#Peaceful", "#Socializer", "#ActiveLifestyle", "#RelaxingVibes", "#FamilyFriendly"])

    st.markdown("#### 🍽️ คุณชอบอาหารแบบไหน?")
    food_pref = st.multiselect("เลือกรูปแบบอาหารที่ชอบ", ["#Foodie", "#BudgetFriendly", "#NightOwl", "#LocalLiving"])

    st.markdown("#### 🚶‍♀️ คุณเดินทางยังไง?")
    transport = st.multiselect("เลือกวิธีเดินทาง", ["#CarFree", "#UrbanLife", "#Traveler", "#TimeSaver"])

    st.markdown("#### 🏃 คุณชอบทำกิจกรรมแบบไหน?")
    activities = st.multiselect("กิจกรรมยามว่างที่คุณชอบ", ["#FitnessLover", "#NatureLover", "#PetFriendly", "#WFH", "#PhotographyLover"])

    st.markdown("#### 🛍️ คุณชอบซื้อของประเภทไหน?")
    shopping = st.multiselect("เลือกสไตล์การช้อปปิ้ง", ["#Shopaholic", "#ConvenienceSeeker", "#LocalLiving"])

    selected_tags = list(set(personality + food_pref + transport + activities + shopping))

    if selected_tags:
        df["match_score"] = df["lifestyle_tags"].apply(lambda tags: match_score(selected_tags, tags))
        matched_df = df[df["match_score"] > 0].sort_values(by="match_score", ascending=False)
        st.markdown(f"### 🔍 พบ {len(matched_df)} หลังที่เข้ากับไลฟ์สไตล์ของคุณ")

        if "swipe_index" not in st.session_state:
            st.session_state.swipe_index = 0

        matched_df = matched_df.reset_index(drop=True)
        if st.session_state.swipe_index < len(matched_df):
            house = matched_df.iloc[st.session_state.swipe_index]
            st.image(house["image_path"], width=500)
            st.write(f"**Address:** {house['address']}")
            st.write(f"**Price:** {house['price']} THB")
            st.write(f"**Style:** {house['style']}, Area: {house['area_size']} sqm")
            st.write(f"**Facilities:** {house['facilities']}")
            st.write(f"**Nearby:** {house['magnet']}")
            st.write(f"**Lifestyle Tags:** {' '.join(house['lifestyle_tags'])}")
            st.write(f"**Match Score:** {house['match_score']:.2f}")

            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("❌ ข้ามบ้านนี้"):
                    st.session_state.swipe_index += 1
                    st.rerun()
            with col2:
                if st.button("❤️ เพิ่มเข้ารายการที่ชอบ"):
                    already = any(fav["image_path"] == house["image_path"] for fav in st.session_state.favorites)
                    if not already:
                        st.session_state.favorites.append(house.to_dict())
                        st.success("✅ เพิ่มบ้านนี้เข้า Favorites แล้ว!")
                    else:
                        st.info("🏷️ บ้านนี้มีอยู่ใน Favorites แล้ว")
                    st.session_state.swipe_index += 1
                    st.rerun()
        else:
            st.info("🏁 You've swiped through all matched houses!")
    else:
        st.info("กรุณาเลือก tag ไลฟ์สไตล์ที่ตรงกับตัวคุณเพื่อเริ่มดูบ้านที่เข้ากันได้ ✨")

if st.session_state.page != "Home" and not st.session_state.selected_house:
    st.markdown("---")
    if st.button("🏠 Return to Home", key="global_home"):
        st.session_state.page = "Home"
        st.rerun()
