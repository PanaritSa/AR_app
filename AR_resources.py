# AR_resources.py
import os
import sqlite3
import pickle
import numpy as np
import pandas as pd
import streamlit as st
from tensorflow.keras.models import load_model
from tensorflow.keras.applications.resnet50 import ResNet50
from tensorflow.keras.layers import GlobalMaxPooling2D
from AR_constants import (
    DB_NAME, CLASSIFIER_PATH, FEATURE_VECTOR_PATH, FILENAMES_PATH
)

def _load_database():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM houses", conn)
    conn.close()
    df["image_path"] = df["image_path"].apply(lambda x: os.path.normpath(x).replace("\\", "/"))
    return df

def _load_models_and_features():
    model_classification = load_model(CLASSIFIER_PATH)
    base_model = ResNet50(weights="imagenet", include_top=False, input_shape=(224, 224, 3))
    base_model.trainable = False
    pooling_layer = GlobalMaxPooling2D()
    feature_list = np.array(pickle.load(open(FEATURE_VECTOR_PATH, "rb")))
    filenames = pickle.load(open(FILENAMES_PATH, "rb"))
    filenames = [os.path.normpath(f).replace("\\", "/") for f in filenames]
    return model_classification, base_model, pooling_layer, feature_list, filenames

def get_resources():
    """Cache heavy resources in session_state for reuse."""
    if "AR_resources" not in st.session_state:
        df = _load_database()
        model_classification, base_model, pooling_layer, feature_list, filenames = _load_models_and_features()
        st.session_state.AR_resources = {
            "df": df,
            "model_classification": model_classification,
            "base_model": base_model,
            "pooling_layer": pooling_layer,
            "feature_list": feature_list,
            "filenames": filenames,
        }
    return st.session_state.AR_resources
