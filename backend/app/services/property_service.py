import math
from datetime import datetime, timedelta

from sqlalchemy import asc, desc, func
from sqlalchemy.orm import Session, joinedload

from app.models import ChatMessage, ChatSession, MessageRole, Prediction, Property, User
from app.schemas import (
    ChatMessageCreate,
    DashboardCharts,
    DashboardSummary,
    PredictionInput,
    PropertyCreate,
    PropertyUpdate,
)
from app.services.ml_service import ml_service
from app.services.rag_service import rag_service


def get_properties(
    db: Session,
    *,
    city: str | None = None,
    min_price: float | None = None,
    max_price: float | None = None,
    bedrooms: int | None = None,
    bathrooms: int | None = None,
    min_area: float | None = None,
    sort: str = "created_desc",
    page: int = 1,
    limit: int = 12,
):
    query = db.query(Property).options(joinedload(Property.images))

    if city:
        query = query.filter(Property.city.ilike(f"%{city}%"))
    if min_price is not None:
        query = query.filter(Property.price >= min_price)
    if max_price is not None:
        query = query.filter(Property.price <= max_price)
    if bedrooms is not None:
        query = query.filter(Property.bedrooms >= bedrooms)
    if bathrooms is not None:
        query = query.filter(Property.bathrooms >= bathrooms)
    if min_area is not None:
        query = query.filter(Property.area_sqft >= min_area)

    sort_map = {
        "price_asc": asc(Property.price),
        "price_desc": desc(Property.price),
        "area_asc": asc(Property.area_sqft),
        "area_desc": desc(Property.area_sqft),
        "created_asc": asc(Property.created_at),
        "created_desc": desc(Property.created_at),
    }
    query = query.order_by(sort_map.get(sort, desc(Property.created_at)))

    total = query.count()
    items = query.offset((page - 1) * limit).limit(limit).all()
    pages = math.ceil(total / limit) if total else 0

    return {"items": items, "total": total, "page": page, "limit": limit, "pages": pages}


def create_property(db: Session, data: PropertyCreate, user: User) -> Property:
    prop = Property(**data.model_dump(), created_by=user.id)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    rag_service.index_property(prop)
    return prop


def update_property(db: Session, prop: Property, data: PropertyUpdate) -> Property:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(prop, field, value)
    db.commit()
    db.refresh(prop)
    rag_service.index_property(prop)
    return prop


def delete_property(db: Session, prop: Property):
    rag_service.remove_property(prop.id)
    db.delete(prop)
    db.commit()


def run_prediction(db: Session, data: PredictionInput, user: User) -> Prediction:
    result = ml_service.predict(data)
    prediction = Prediction(
        user_id=user.id,
        property_id=data.property_id,
        input_features=result["input_features"],
        predicted_price=result["predicted_price"],
        confidence_score=result["confidence_score"],
        shap_values={"contributions": result["shap_contributions"]},
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction, result


def create_chat_session(db: Session, user: User, title: str = "New Chat") -> ChatSession:
    session = ChatSession(user_id=user.id, title=title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def add_chat_message(db: Session, session: ChatSession, data: ChatMessageCreate) -> tuple[ChatMessage, ChatMessage]:
    user_message = ChatMessage(
        session_id=session.id, role=MessageRole.user, content=data.content
    )
    db.add(user_message)
    db.flush()

    retrieved = rag_service.retrieve(data.content)
    answer, context = rag_service.generate_response(data.content, retrieved)

    assistant_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.assistant,
        content=answer,
        retrieved_context={"sources": context},
    )
    db.add(assistant_message)

    if session.title == "New Chat":
        session.title = data.content[:50]

    db.commit()
    db.refresh(user_message)
    db.refresh(assistant_message)
    return user_message, assistant_message


def get_dashboard_summary(db: Session) -> DashboardSummary:
    total_properties = db.query(func.count(Property.id)).scalar() or 0
    price_stats = db.query(
        func.avg(Property.price),
        func.max(Property.price),
        func.min(Property.price),
    ).one()

    total_predictions = db.query(func.count(Prediction.id)).scalar() or 0
    avg_predicted = db.query(func.avg(Prediction.predicted_price)).scalar() or 0

    return DashboardSummary(
        total_properties=total_properties,
        average_price=round(float(price_stats[0] or 0), 2),
        highest_price=round(float(price_stats[1] or 0), 2),
        lowest_price=round(float(price_stats[2] or 0), 2),
        total_predictions=total_predictions,
        average_predicted_price=round(float(avg_predicted), 2),
    )


def get_dashboard_charts(db: Session) -> DashboardCharts:
    city_rows = (
        db.query(Property.city, func.count(Property.id))
        .group_by(Property.city)
        .order_by(desc(func.count(Property.id)))
        .limit(10)
        .all()
    )

    properties = db.query(Property.price).all()
    buckets = [
        ("Under ₹50L", 0, 5_000_000),
        ("₹50L - ₹1Cr", 5_000_000, 10_000_000),
        ("₹1Cr - ₹2Cr", 10_000_000, 20_000_000),
        ("Above ₹2Cr", 20_000_000, float("inf")),
    ]
    price_distribution = []
    for label, low, high in buckets:
        count = sum(1 for (price,) in properties if low <= float(price) < high)
        price_distribution.append({"range_label": label, "count": count})

    recent_listings = (
        db.query(Property)
        .options(joinedload(Property.images))
        .order_by(desc(Property.created_at))
        .limit(5)
        .all()
    )

    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    trend_rows = (
        db.query(func.date(Prediction.created_at), func.count(Prediction.id))
        .filter(Prediction.created_at >= thirty_days_ago)
        .group_by(func.date(Prediction.created_at))
        .order_by(func.date(Prediction.created_at))
        .all()
    )
    prediction_trend = [
        {"date": str(row[0]), "count": row[1]} for row in trend_rows
    ]

    return DashboardCharts(
        properties_by_city=[{"city": c, "count": n} for c, n in city_rows],
        price_distribution=price_distribution,
        recent_listings=recent_listings,
        prediction_trend=prediction_trend,
    )
