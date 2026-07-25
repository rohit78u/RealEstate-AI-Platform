from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore",
    )

    database_url: str = "sqlite:///./app.db"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    # Groq API Key
    groq_api_key: str = ""

    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    upload_dir: str = "./uploads"
    chroma_persist_dir: str = "./chroma_db"
    ml_artifacts_dir: str = "./app/ml/artifacts"

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


settings = Settings()