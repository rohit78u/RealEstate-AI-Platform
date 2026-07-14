import enum
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    user = "user"


class MessageRole(str, enum.Enum):
    user = "user"
    assistant = "assistant"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.user, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    properties: Mapped[list["Property"]] = relationship(back_populates="creator")
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="user")
    chat_sessions: Mapped[list["ChatSession"]] = relationship(back_populates="user")


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    bedrooms: Mapped[int] = mapped_column(Integer, nullable=False)
    bathrooms: Mapped[int] = mapped_column(Integer, nullable=False)
    area_sqft: Mapped[float] = mapped_column(Float, nullable=False)
    floors: Mapped[int] = mapped_column(Integer, default=1)
    year_built: Mapped[int] = mapped_column(Integer, nullable=False)
    parking: Mapped[int] = mapped_column(Integer, default=0)
    city: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    location: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    features: Mapped[dict | None] = mapped_column(JSON)
    created_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    creator: Mapped["User | None"] = relationship(back_populates="properties")
    images: Mapped[list["PropertyImage"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    predictions: Mapped[list["Prediction"]] = relationship(back_populates="property")


class PropertyImage(Base):
    __tablename__ = "property_images"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    property_id: Mapped[int] = mapped_column(ForeignKey("properties.id", ondelete="CASCADE"))
    image_path: Mapped[str] = mapped_column(String(500), nullable=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    property: Mapped["Property"] = relationship(back_populates="images")


class Prediction(Base):
    __tablename__ = "predictions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    property_id: Mapped[int | None] = mapped_column(ForeignKey("properties.id"), nullable=True)
    input_features: Mapped[dict] = mapped_column(JSON, nullable=False)
    predicted_price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=False)
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    shap_values: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="predictions")
    property: Mapped["Property | None"] = relationship(back_populates="predictions")


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(255), default="New Chat")
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="chat_sessions")
    messages: Mapped[list["ChatMessage"]] = relationship(
        back_populates="session", cascade="all, delete-orphan"
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("chat_sessions.id", ondelete="CASCADE"))
    role: Mapped[MessageRole] = mapped_column(Enum(MessageRole), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    retrieved_context: Mapped[dict | None] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    session: Mapped["ChatSession"] = relationship(back_populates="messages")
