# backend/app/services/categorizer.py
from transformers import pipeline

# Load zero-shot classification model once at startup
# (Tip: use the smaller one below if you're low on space)
classifier = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")
# classifier = pipeline("zero-shot-classification", model="valhalla/distilbart-mnli-12-3")

# Emission activity categories (used to determine emission factors)
CATEGORY_LABELS = [
    "electricity",
    "natural_gas",
    "diesel",
    "gasoline",
    "district_heat",
    "air_travel",
    "hotel",
    "rail_travel",
    "last_mile_taxi_ridehail",
    "employee_commute",
    "cloud_compute",
    "purchased_goods",
    "waste_landfill",
    "refrigerants"
]

# GHG Protocol scopes (1, 2, 3)
SCOPE_LABELS = [
    "Scope 1", #Direct emissions from owned or controlled sources (fuel, refrigerants)",
    "Scope 2", # Indirect emissions from purchased electricity, steam, heating, or cooling",
    "Scope 3" #Other indirect emissions (business travel, commuting, purchased goods, waste)"
]


def predict_category_and_scope(description: str):
    """
    Predict both emission category and scope using zero-shot classification.
    """
    # Predict emission category
    cat_result = classifier(description, CATEGORY_LABELS)
    category = cat_result["labels"][0]
    cat_confidence = cat_result["scores"][0]

    # Predict emission scope
    scope_result = classifier(description, SCOPE_LABELS)
    scope = scope_result["labels"][0]
    scope_confidence = scope_result["scores"][0]

    return {
        "predicted_category": category,
        "category_confidence": cat_confidence,
        "predicted_scope": scope,
        "scope_confidence": scope_confidence
    }
