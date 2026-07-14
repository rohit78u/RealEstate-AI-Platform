from datetime import datetime
from typing import Any

from pydantic import BaseModel, EmailStr, Field

from app.models import MessageRole, UserRole


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    user_id: int
    role: UserRole


class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    full_name: str = Field(min_length=2)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: UserRole
    created_at: datetime

    class Config:
        from_attributes = True


class PropertyImageResponse(BaseModel):
    id: int
    image_path: str
    is_primary: bool

    class Config:
        from_attributes = True


class PropertyBase(BaseModel):
    title: str
    description: str | None = None
    price: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    bathrooms: int = Field(ge=0)
    area_sqft: float = Field(gt=0)
    floors: int = Field(ge=1, default=1)
    year_built: int = Field(ge=1800, le=2100)
    parking: int = Field(ge=0, default=0)
    city: str
    location: str
    features: dict[str, Any] | None = None


class PropertyCreate(PropertyBase):
    pass


class PropertyUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    price: float | None = Field(default=None, gt=0)
    bedrooms: int | None = Field(default=None, ge=0)
    bathrooms: int | None = Field(default=None, ge=0)
    area_sqft: float | None = Field(default=None, gt=0)
    floors: int | None = Field(default=None, ge=1)
    year_built: int | None = Field(default=None, ge=1800, le=2100)
    parking: int | None = Field(default=None, ge=0)
    city: str | None = None
    location: str | None = None
    features: dict[str, Any] | None = None


class PropertyResponse(PropertyBase):
    id: int
    created_by: int | None
    created_at: datetime
    images: list[PropertyImageResponse] = []

    class Config:
        from_attributes = True


class PropertyListResponse(BaseModel):
    items: list[PropertyResponse]
    total: int
    page: int
    limit: int
    pages: int


class PredictionInput(BaseModel):
    city: str
    location: str
    area_sqft: float = Field(gt=0)
    bedrooms: int = Field(ge=0)
    bathrooms: int = Field(ge=0)
    floors: int = Field(ge=1, default=1)
    year_built: int = Field(ge=1800, le=2100)
    parking: int = Field(ge=0, default=0)
    property_id: int | None = None


class ShapContribution(BaseModel):
    feature: str
    impact: float
    direction: str


class PredictionResponse(BaseModel):
    id: int
    predicted_price: float
    confidence_score: float
    shap_contributions: list[ShapContribution]
    explanation: str
    created_at: datetime

    class Config:
        from_attributes = True


class ChatMessageCreate(BaseModel):
    content: str = Field(min_length=1)


class ChatMessageResponse(BaseModel):
    id: int
    role: MessageRole
    content: str
    retrieved_context: dict | None
    created_at: datetime

    class Config:
        from_attributes = True


class ChatSessionResponse(BaseModel):
    id: int
    title: str
    created_at: datetime
    messages: list[ChatMessageResponse] = []

    class Config:
        from_attributes = True


class DashboardSummary(BaseModel):
    total_properties: int
    average_price: float
    highest_price: float
    lowest_price: float
    total_predictions: int
    average_predicted_price: float


class CityCount(BaseModel):
    city: str
    count: int


class PriceBucket(BaseModel):
    range_label: str
    count: int


class DashboardCharts(BaseModel):
    properties_by_city: list[CityCount]
    price_distribution: list[PriceBucket]
    recent_listings: list[PropertyResponse]
    prediction_trend: list[dict[str, Any]]
