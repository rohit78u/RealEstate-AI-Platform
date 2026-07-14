from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, chat, dashboard, predictions, properties
from app.config import settings
from app.database import Base, engine
from app.models import User, UserRole
from app.database import SessionLocal
from app.utils.security import hash_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    yield


def _seed_admin():
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == "admin@realestate.com").first()
        if not admin:
            admin = User(
                email="admin@realestate.com",
                password_hash=hash_password("admin123"),
                full_name="Platform Admin",
                role=UserRole.admin,
            )
            db.add(admin)
            db.commit()
    finally:
        db.close()


app = FastAPI(
    title="AI Real Estate Intelligence Platform",
    description="Browse properties, predict prices with ML, and chat with an AI assistant.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

upload_path = Path(settings.upload_dir)
upload_path.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(upload_path)), name="uploads")

app.include_router(auth.router, prefix="/api")
app.include_router(properties.router, prefix="/api")
app.include_router(predictions.router, prefix="/api")
app.include_router(chat.router, prefix="/api")
app.include_router(dashboard.router, prefix="/api")


@app.get("/api/health")
def health_check():
    from app.services.ml_service import ml_service

    return {
        "status": "healthy",
        "ml_model_ready": ml_service.is_ready(),
    }
