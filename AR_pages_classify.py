# AR_pages_classify.py
import streamlit as st
from PIL import Image
from AR_images import correct_orientation, pad_to_square
from AR_features import get_similar_images_from_upload
from AR_constants import IMAGE_SIZE
from AR_pagination import paginate_results
import numpy as np
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

def render_classify(df, model_classification, base_model, pooling_layer, feature_list, filenames):
    st.subheader("📷 Upload an Image for Classification")
    uploaded_file = st.file_uploader("Choose an image...", type=["jpg", "jpeg", "png"])
    if uploaded_file:
        image = Image.open(uploaded_file)
        image = correct_orientation(image)
        image = pad_to_square(image).resize(IMAGE_SIZE)

        img_array = img_to_array(image)
        img_array = np.expand_dims(img_array, axis=0)
        img_array = preprocess_input(img_array)
        pred = model_classification.predict(img_array)[0]

        style_labels = df["style"].unique()
        top_idx = np.argsort(pred)[-3:][::-1]
        top_styles = [(style_labels[i], pred[i] * 100) for i in top_idx]

        st.image(image, width=300)
        st.subheader("🎨 Top 3 Predicted Styles")
        st.session_state.classify_results = {}
        for s, score in top_styles:
            st.write(f"✅ {s}: {score:.2f}%")
            st.session_state.classify_results[s] = df[df["style"] == s]

        similar_image_paths = get_similar_images_from_upload(image, base_model, pooling_layer, feature_list, filenames, IMAGE_SIZE)
        sim_df = df[df["image_path"].isin(similar_image_paths)]
        st.write("## 🏡 Top 20 Similar Houses Based on Uploaded Image")
        paginated = paginate_results(sim_df, page_key="upload_similar")
        for i, (_, row) in enumerate(paginated.iterrows()):
            st.image(row["image_path"], caption=row["style"], width=300)
            if st.button(f"View Details: {row['address']}", key=f"upload_similar_{i}"):
                st.session_state.selected_house = row.to_dict()
                st.session_state.return_page = "Classify"
                st.rerun()

    for s, style_df in st.session_state.get("classify_results", {}).items():
        if not style_df.empty:
            st.write(f"### 🏘 Houses in style: {s}")
            paginated = paginate_results(style_df, page_key=f"classify_page_{s}")
            for i, (_, row) in enumerate(paginated.iterrows()):
                st.image(row["image_path"], caption=row["style"], width=300)
                if st.button(f"View Details: {row['address']}", key=f"classify_{s}_{i}"):
                    st.session_state.selected_house = row.to_dict()
                    st.session_state.return_page = "Classify"
                    st.rerun()
