from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Prediction, User
from app.schemas import PredictionInput, PredictionResponse, ShapContribution
from app.services.ml_service import ml_service
from app.services.property_service import run_prediction
from app.utils.security import get_current_user

router = APIRouter(prefix="/predictions", tags=["Predictions"])


@router.post("", response_model=PredictionResponse)
def predict_price(
    data: PredictionInput,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not ml_service.is_ready():
        raise HTTPException(
            status_code=503,
            detail="ML model not available. Run the training script: python -m app.ml.train",
        )

    prediction, result = run_prediction(db, data, current_user)
    return PredictionResponse(
        id=prediction.id,
        predicted_price=result["predicted_price"],
        confidence_score=result["confidence_score"],
        shap_contributions=[ShapContribution(**c) for c in result["shap_contributions"]],
        explanation=result["explanation"],
        created_at=prediction.created_at,
    )


@router.get("/history", response_model=list[PredictionResponse])
def prediction_history(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    predictions = (
        db.query(Prediction)
        .filter(Prediction.user_id == current_user.id)
        .order_by(Prediction.created_at.desc())
        .limit(20)
        .all()
    )

    results = []
    for p in predictions:
        contributions = []
        if p.shap_values and "contributions" in p.shap_values:
            contributions = [ShapContribution(**c) for c in p.shap_values["contributions"]]

        results.append(
            PredictionResponse(
                id=p.id,
                predicted_price=float(p.predicted_price),
                confidence_score=p.confidence_score,
                shap_contributions=contributions,
                explanation=f"Predicted price: ₹{float(p.predicted_price):,.0f}",
                created_at=p.created_at,
            )
        )
    return results
