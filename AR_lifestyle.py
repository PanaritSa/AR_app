# AR_lifestyle.py
import pandas as pd

MAGNET_TO_LIFESTYLE = {
    "Hospital": ["#FamilyFriendly", "#SeniorLiving", "#HealthConscious"],
    "School": ["#FamilyFriendly", "#Peaceful", "#EducationOriented"],
    "Shopping Mall": ["#UrbanLife", "#Shopaholic", "#ConvenienceSeeker"],
    "Park": ["#NatureLover", "#ActiveLifestyle", "#PetFriendly"],
    "Public Transport": ["#CarFree", "#UrbanLife", "#Traveler"],
    "University": ["#StudentLife", "#YoungProfessional", "#AcademicLifestyle"],
    "Market": ["#LocalLiving", "#Foodie", "#BudgetFriendly"],
    "Office Building": ["#Workaholic", "#TimeSaver", "#ProfessionalLifestyle"],
    "Restaurant Hub": ["#Foodie", "#NightOwl", "#Socializer"],
    "Cultural Site": ["#ArtLover", "#HistoryBuff", "#PhotographyLover"]
}

FACILITY_TO_LIFESTYLE = {
    "Pool, Gym, Parking": ["#HealthConscious", "#FamilyFriendly", "#FitnessLover"],
    "Garden, Security": ["#NatureLover", "#SafeLiving", "#RelaxingVibes"],
    "Balcony, Kitchen": ["#WFH", "#ChefLife", "#SunlightLover"],
    "Smart Home, CCTV": ["#TechSavvy", "#SafeLiving", "#ModernLifestyle"]
}

def extract_lifestyle_tags(magnet_str, facilities_str):
    tags = set()
    if pd.notna(magnet_str):
        for m in magnet_str.split(","):
            tags.update(MAGNET_TO_LIFESTYLE.get(m.strip(), []))
    if pd.notna(facilities_str):
        for fac_key, fac_tags in FACILITY_TO_LIFESTYLE.items():
            if all(f.strip() in facilities_str for f in fac_key.split(",")):
                tags.update(fac_tags)
    return list(tags)

def match_score(user_tags, house_tags):
    if not user_tags or not house_tags:
        return 0.0
    return len(set(user_tags) & set(house_tags)) / len(set(user_tags))
