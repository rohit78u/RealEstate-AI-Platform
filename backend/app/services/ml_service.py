import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import shap
from xgboost import XGBRegressor

from app.config import settings
from app.schemas import PredictionInput, ShapContribution

FEATURE_COLUMNS = [
    "area_sqft",
    "bedrooms",
    "bathrooms",
    "floors",
    "year_built",
    "parking",
    "house_age",
    "city",
    "location",
]


class MLService:
    def __init__(self):
        self.model: XGBRegressor | None = None
        self.preprocessor = None
        self.feature_names: list[str] = []
        self.residual_std: float = 0.0
        self._explainer: shap.TreeExplainer | None = None
        self._load_artifacts()

    def _artifacts_path(self) -> Path:
        return Path(settings.ml_artifacts_dir)

    def _load_artifacts(self):
        artifacts = self._artifacts_path()
        model_path = artifacts / "model.joblib"
        preprocessor_path = artifacts / "preprocessor.joblib"
        meta_path = artifacts / "metadata.json"

        if not model_path.exists() or not preprocessor_path.exists():
            return

        self.model = joblib.load(model_path)
        self.preprocessor = joblib.load(preprocessor_path)
        if meta_path.exists():
            with open(meta_path) as f:
                meta = json.load(f)
                self.feature_names = meta.get("feature_names", [])
                self.residual_std = meta.get("residual_std", 0.0)
        if self.model is not None:
            self._explainer = shap.TreeExplainer(self.model)

    def is_ready(self) -> bool:
        return self.model is not None and self.preprocessor is not None

    def _prepare_features(self, data: PredictionInput) -> pd.DataFrame:
        current_year = 2026
        row = {
            "area_sqft": data.area_sqft,
            "bedrooms": data.bedrooms,
            "bathrooms": data.bathrooms,
            "floors": data.floors,
            "year_built": data.year_built,
            "parking": data.parking,
            "house_age": current_year - data.year_built,
            "city": data.city,
            "location": data.location,
        }
        return pd.DataFrame([row])

    def predict(self, data: PredictionInput) -> dict:
        if not self.is_ready():
            raise RuntimeError("ML model not trained. Run training script first.")

        df = self._prepare_features(data)
        X = self.preprocessor.transform(df)
        predicted_price = float(self.model.predict(X)[0])

        shap_values = self._explainer.shap_values(X)
        contributions = self._format_shap(shap_values[0], df.iloc[0])
        confidence = self._compute_confidence(predicted_price)
        explanation = self._generate_explanation(predicted_price, contributions)

        return {
            "predicted_price": round(predicted_price, 2),
            "confidence_score": confidence,
            "shap_contributions": contributions,
            "explanation": explanation,
            "input_features": df.iloc[0].to_dict(),
        }

    def _format_shap(self, shap_row: np.ndarray, raw_row: pd.Series) -> list[dict]:
        if not self.feature_names:
            return []

        pairs = sorted(
            zip(self.feature_names, shap_row),
            key=lambda x: abs(x[1]),
            reverse=True,
        )[:6]

        contributions = []
        for feature, impact in pairs:
            display_name = feature.replace("_", " ").title()
            if feature in raw_row.index:
                display_name = f"{display_name} ({raw_row[feature]})"
            contributions.append(
                {
                    "feature": display_name,
                    "impact": round(float(impact), 2),
                    "direction": "positive" if impact >= 0 else "negative",
                }
            )
        return contributions

    def _compute_confidence(self, predicted_price: float) -> float:
        if self.residual_std <= 0:
            return 0.75
        relative_error = self.residual_std / max(predicted_price, 1)
        confidence = max(0.5, min(0.99, 1 - relative_error))
        return round(confidence, 2)

    def _generate_explanation(self, price: float, contributions: list[dict]) -> str:
        formatted_price = f"₹{price:,.0f}"
        if not contributions:
            return f"Estimated price is {formatted_price} based on the provided property features."

        top = contributions[:3]
        parts = []
        for item in top:
            sign = "+" if item["direction"] == "positive" else "-"
            parts.append(f"{item['feature']}: {sign}₹{abs(item['impact']):,.0f}")

        return (
            f"Estimated price is {formatted_price}. "
            f"Top contributing features: {'; '.join(parts)}."
        )


ml_service = MLService()
