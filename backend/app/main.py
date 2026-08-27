from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api import auth, chat, dashboard, predictions, properties
from app.config import settings
from app.database import Base, SessionLocal, engine
from app.models import User, UserRole
from app.utils.security import hash_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    _seed_admin()
    yield


def _seed_admin():
    """Create the bootstrap admin only when credentials are explicitly configured."""
    if not settings.admin_email or not settings.admin_password:
        return

    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.email == settings.admin_email).first()
        if not admin:
            admin = User(
                email=settings.admin_email,
                password_hash=hash_password(settings.admin_password),
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
