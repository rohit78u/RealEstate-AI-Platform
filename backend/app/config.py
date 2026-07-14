from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mysql+pymysql://root:rootpassword@localhost:3306/realestate"
    jwt_secret: str = "dev-secret-change-in-production"
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    gemini_api_key: str = ""
    cors_origins: str = "http://localhost:5173,http://localhost:3000"
    upload_dir: str = "./uploads"
    chroma_persist_dir: str = "./chroma_db"
    ml_artifacts_dir: str = "./app/ml/artifacts"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
