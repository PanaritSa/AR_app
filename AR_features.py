# AR_features.py
import os
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from tensorflow.keras.applications.resnet50 import preprocess_input
from tensorflow.keras.preprocessing.image import img_to_array

def get_recommendations(image_path, filenames, feature_list, topk=5):
    image_path = os.path.normpath(image_path).replace("\\", "/")
    try:
        index = filenames.index(image_path)
    except ValueError:
        return []
    query_feature = feature_list[index].reshape(1, -1)
    similarities = cosine_similarity(feature_list, query_feature).flatten()
    indices = np.argsort(similarities)[-(topk+1):-1][::-1]
    return [filenames[i] for i in indices]

def get_similar_images_from_upload(pil_image, base_model, pooling_layer, feature_list, filenames, image_size):
    image = pil_image.resize(image_size)
    img_array = img_to_array(image)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = preprocess_input(img_array)
    feature_map = base_model.predict(img_array)
    features = pooling_layer(feature_map).numpy()
    similarities = cosine_similarity(feature_list, features).flatten()
    indices = np.argsort(similarities)[-20:][::-1]
    return [filenames[i] for i in indices]
