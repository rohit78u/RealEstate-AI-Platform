from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    # ============================================================
    # DATABASE
    # ============================================================

    database_url: str = "sqlite:///./app.db"

    # ============================================================
    # JWT AUTHENTICATION
    # ============================================================

    jwt_secret: str = "change-this-secret-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # ============================================================
    # ADMIN
    # ============================================================

    admin_email: str = ""
    admin_password: str = ""

    # ============================================================
    # GROQ LLM
    # ============================================================

    groq_api_key: str = ""
    groq_model: str = "openai/gpt-oss-20b"

    # ============================================================
    # CORS
    # ============================================================

    cors_origins: str = (
        "http://localhost:5173,"
        "http://localhost:3000"
    )

    # ============================================================
    # STORAGE
    # ============================================================

    upload_dir: str = "./uploads"
    chroma_persist_dir: str = "./chroma_db"
    ml_artifacts_dir: str = "./app/ml/artifacts"

    # ============================================================
    # HELPERS
    # ============================================================

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()
