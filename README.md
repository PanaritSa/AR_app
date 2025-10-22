# AR_app

# House Finder (AR Modular)

## Run
1. Put your data files in the project root: `house_database.db`, `best_model13cls.keras`, `featurevector.pkl`, `filenames.pkl`.
2. Optional: replace `assets/H_vector.jpg` with your own hero image.
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Start app:
   ```bash
   streamlit run AR_app.py
   ```

## Files
- `AR_app.py`: main entry and routing
- `AR_constants.py`: constants and paths
- `AR_resources.py`: DB and model loading (cached)
- `AR_images.py`: image utilities (EXIF fix, pad-to-square)
- `AR_features.py`: recommendation + upload similarity
- `AR_lifestyle.py`: lifestyle mapping + scoring
- `AR_pagination.py`: pagination widget
- `AR_map.py`: folium map + radius filter
- `AR_ui.py`: shared UI components (menu, detail view)
- `AR_pages_*.py`: individual page renderers
