"""Train XGBoost house price model with synthetic Indian real estate data."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from xgboost import XGBRegressor

CITIES = ["Mumbai", "Delhi", "Bangalore", "Pune", "Hyderabad", "Chennai"]
LOCATIONS = {
    "Mumbai": ["Bandra", "Andheri", "Powai", "Worli"],
    "Delhi": ["Dwarka", "Saket", "Rohini", "Connaught Place"],
    "Bangalore": ["Koramangala", "Indiranagar", "Whitefield", "HSR Layout"],
    "Pune": ["Koregaon Park", "Hinjewadi", "Baner", "Kothrud"],
    "Hyderabad": ["Gachibowli", "Banjara Hills", "Madhapur", "Kondapur"],
    "Chennai": ["Adyar", "Velachery", "OMR", "T Nagar"],
}

CITY_MULTIPLIER = {
    "Mumbai": 1.4,
    "Delhi": 1.2,
    "Bangalore": 1.15,
    "Pune": 0.95,
    "Hyderabad": 0.9,
    "Chennai": 0.85,
}


def generate_dataset(n_samples: int = 2000) -> pd.DataFrame:
    rng = np.random.default_rng(42)
    rows = []
    current_year = 2026

    for _ in range(n_samples):
        city = rng.choice(CITIES)
        location = rng.choice(LOCATIONS[city])
        area = rng.integers(600, 3500)
        bedrooms = rng.integers(1, 6)
        bathrooms = max(1, bedrooms - rng.integers(0, 2))
        floors = rng.integers(1, 4)
        year_built = rng.integers(1990, current_year)
        parking = rng.integers(0, 3)
        house_age = current_year - year_built

        base_price = area * 4500
        base_price += bedrooms * 300000
        base_price += bathrooms * 150000
        base_price += parking * 200000
        base_price -= house_age * 50000
        base_price *= CITY_MULTIPLIER[city]
        base_price += rng.normal(0, base_price * 0.08)

        rows.append(
            {
                "area_sqft": area,
                "bedrooms": bedrooms,
                "bathrooms": bathrooms,
                "floors": floors,
                "year_built": year_built,
                "parking": parking,
                "house_age": house_age,
                "city": city,
                "location": location,
                "price": max(base_price, 2_000_000),
            }
        )

    return pd.DataFrame(rows)


def build_preprocessor() -> ColumnTransformer:
    numeric_features = [
        "area_sqft",
        "bedrooms",
        "bathrooms",
        "floors",
        "year_built",
        "parking",
        "house_age",
    ]
    categorical_features = ["city", "location"]

    return ColumnTransformer(
        transformers=[
            ("num", StandardScaler(), numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )


def train():
    print("Generating synthetic training data...")
    df = generate_dataset(2500)

    X = df.drop(columns=["price"])
    y = df["price"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    preprocessor = build_preprocessor()
    X_train_processed = preprocessor.fit_transform(X_train)
    X_test_processed = preprocessor.transform(X_test)

    feature_names = (
        ["area_sqft", "bedrooms", "bathrooms", "floors", "year_built", "parking", "house_age"]
        + list(preprocessor.named_transformers_["cat"].get_feature_names_out(["city", "location"]))
    )

    model = XGBRegressor(
        n_estimators=300,
        max_depth=6,
        learning_rate=0.08,
        subsample=0.9,
        colsample_bytree=0.9,
        random_state=42,
    )
    model.fit(X_train_processed, y_train)

    predictions = model.predict(X_test_processed)
    rmse = np.sqrt(mean_squared_error(y_test, predictions))
    mae = mean_absolute_error(y_test, predictions)
    r2 = r2_score(y_test, predictions)
    residuals = y_test - predictions
    residual_std = float(np.std(residuals))

    print(f"RMSE: ₹{rmse:,.0f}")
    print(f"MAE:  ₹{mae:,.0f}")
    print(f"R²:   {r2:.4f}")

    artifacts_dir = Path(__file__).parent / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    joblib.dump(model, artifacts_dir / "model.joblib")
    joblib.dump(preprocessor, artifacts_dir / "preprocessor.joblib")

    with open(artifacts_dir / "metadata.json", "w") as f:
        json.dump({"feature_names": feature_names, "residual_std": residual_std}, f, indent=2)

    print(f"Model saved to {artifacts_dir}")


if __name__ == "__main__":
    train()
