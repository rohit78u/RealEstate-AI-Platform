import math
from datetime import datetime, timedelta

#from backend.app.api import properties
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


def validate_bedroom_bathroom(bedrooms: int, bathrooms: int) -> None:
    if bathrooms >= bedrooms:
        raise ValueError("Bathrooms must be fewer than bedrooms")


def create_property(db: Session, data: PropertyCreate, user: User) -> Property:
    validate_bedroom_bathroom(data.bedrooms, data.bathrooms)
    prop = Property(**data.model_dump(), created_by=user.id)
    db.add(prop)
    db.commit()
    db.refresh(prop)
    rag_service.index_property(prop)
    return prop


def update_property(db: Session, prop: Property, data: PropertyUpdate) -> Property:
    changes = data.model_dump(exclude_unset=True)
    bedrooms = changes.get("bedrooms", prop.bedrooms)
    bathrooms = changes.get("bathrooms", prop.bathrooms)
    validate_bedroom_bathroom(bedrooms, bathrooms)
    for field, value in changes.items():
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
    db.flush()

    welcome_text = (
        "Welcome to the AI Real Estate Assistant. "
        "Ask me about properties, budgets, locations, features, comparisons, or recommendations, "
        "and I’ll help you find the best options from our current listings."
    )

    assistant_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.assistant,
        content=welcome_text,
        retrieved_context=None,
    )
    db.add(assistant_message)

    db.commit()
    db.refresh(session)
    return session


def add_chat_message(
    db: Session,
    session: ChatSession,
    data: ChatMessageCreate,
) -> tuple[ChatMessage, ChatMessage]:

    # Save user's message
    user_message = ChatMessage(
        session_id=session.id,
        role=MessageRole.user,
        content=data.content,
    )
    db.add(user_message)
    db.flush()

    # Load ALL properties from database
    properties = db.query(Property).all()

    # Convert every property into RAG context
    all_context = rag_service.properties_to_context(properties)

    # Retrieve most relevant properties from Chroma
    retrieved = rag_service.retrieve(
        data.content,
        top_k=300,
    )

    # Merge retrieved properties with full database context
    merged = {}

    for item in retrieved:
        merged[item["metadata"]["property_id"]] = item

    for item in all_context:
        merged.setdefault(item["metadata"]["property_id"], item)

    final_context = list(merged.values())

    # Generate response
    answer, context = rag_service.generate_response(
        data.content,
        final_context,
    )

    # Save assistant response
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
        func.avg(Property.area_sqft),
    ).one()

    total_area = float(db.query(func.sum(Property.area_sqft)).scalar() or 0)
    total_price = float(db.query(func.sum(Property.price)).scalar() or 0)
    average_price_per_sqft = round(total_price / total_area, 2) if total_area > 0 else 0

    price_values = [float(price) for (price,) in db.query(Property.price).order_by(Property.price).all()]
    median_price = 0.0
    if price_values:
        mid = len(price_values) // 2
        if len(price_values) % 2 == 1:
            median_price = price_values[mid]
        else:
            median_price = (price_values[mid - 1] + price_values[mid]) / 2

    # median price per sqft
    pps_values = [float(p[0]) / float(p[1]) for p in db.query(Property.price, Property.area_sqft).filter(Property.area_sqft > 0).all()]
    median_price_per_sqft = 0.0
    if pps_values:
        pps_values.sort()
        mid = len(pps_values) // 2
        if len(pps_values) % 2 == 1:
            median_price_per_sqft = pps_values[mid]
        else:
            median_price_per_sqft = (pps_values[mid - 1] + pps_values[mid]) / 2

    total_predictions = db.query(func.count(Prediction.id)).scalar() or 0
    avg_predicted = db.query(func.avg(Prediction.predicted_price)).scalar() or 0

    return DashboardSummary(
        total_properties=total_properties,
        total_area=round(total_area, 2),
        average_area=round(float(price_stats[3] or 0), 2),
        average_price=round(float(price_stats[0] or 0), 2),
        median_price=round(median_price, 2),
        median_price_per_sqft=round(median_price_per_sqft, 2),
        average_price_per_sqft=average_price_per_sqft,
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

    bedroom_rows = (
        db.query(Property.bedrooms, func.count(Property.id))
        .group_by(Property.bedrooms)
        .order_by(Property.bedrooms)
        .all()
    )

    # Build dynamic price distribution buckets based on data quartiles so
    # the chart scale adapts to the current dataset instead of fixed ranges.
    raw_prices = [float(p[0]) for p in db.query(Property.price).filter(Property.price != None).all()]
    price_distribution = []
    if not raw_prices:
        # no data -> return empty buckets
        price_distribution = [
            {"range_label": "No data", "count": 0},
        ]
    else:
        raw_prices.sort()
        n = len(raw_prices)
        def percentile(p):
            # simple linear interpolation for percentiles
            if n == 1:
                return raw_prices[0]
            k = (n - 1) * p
            f = int(k)
            c = min(f + 1, n - 1)
            if f == c:
                return raw_prices[int(k)]
            d0 = raw_prices[f] * (c - k)
            d1 = raw_prices[c] * (k - f)
            return (d0 + d1)

        p0 = raw_prices[0]
        p25 = percentile(0.25)
        p50 = percentile(0.5)
        p75 = percentile(0.75)
        p100 = raw_prices[-1]

        thresholds = [p0, p25, p50, p75, p100]

        def rupee_label(v: float) -> str:
            return f"₹{int(v):,}"

        buckets = []
        for i in range(len(thresholds) - 1):
            low = thresholds[i]
            high = thresholds[i + 1]
            if i == 0:
                label = f"Under {rupee_label(high)}"
            elif i == len(thresholds) - 2:
                label = f"{rupee_label(low)} - {rupee_label(high)}"
            else:
                label = f"{rupee_label(low)} - {rupee_label(high)}"
            buckets.append((label, low, high))

        # Last bucket label (above third quartile)
        buckets[-1] = (f"Above {rupee_label(thresholds[-2])}", thresholds[-2], float("inf"))

        for label, low, high in buckets:
            if high == float("inf"):
                count = sum(1 for price in raw_prices if float(price) >= low)
            else:
                count = sum(1 for price in raw_prices if low <= float(price) < high)
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

    # Average price per sqft by city
    city_price_rows = (
        db.query(Property.city, func.avg(Property.price / Property.area_sqft))
        .filter(Property.area_sqft > 0)
        .group_by(Property.city)
        .order_by(desc(func.avg(Property.price / Property.area_sqft)))
        .limit(10)
        .all()
    )

    price_per_sqft_by_city = [
        {"city": c, "average_price_per_sqft": round(float(v or 0), 2)} for c, v in city_price_rows
    ]

    # Top 5 most expensive properties
    top_expensive = (
        db.query(Property.id, Property.title, Property.city, Property.price)
        .order_by(desc(Property.price))
        .limit(5)
        .all()
    )

    top_expensive_list = [
        {"id": int(r[0]), "title": r[1], "city": r[2], "price": float(r[3])} for r in top_expensive
    ]

    return DashboardCharts(
        properties_by_city=[{"city": c, "count": n} for c, n in city_rows],
        property_bedroom_distribution=[{"bedrooms": int(b), "count": n} for b, n in bedroom_rows],
        price_distribution=price_distribution,
        recent_listings=recent_listings,
        prediction_trend=prediction_trend,
        price_per_sqft_by_city=price_per_sqft_by_city,
        top_expensive=top_expensive_list,
    )
