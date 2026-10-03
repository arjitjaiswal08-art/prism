import os

class Settings:
    PROJECT_NAME: str = "Prism LGBTQ+ Privacy-First Platform"
    VERSION: str = "1.0.0"
    
    # Database: Defaults to SQLite for instant local execution, supports PostgreSQL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./prism.db")
    
    # JWT Security Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "prism-super-secret-crypto-key-change-in-prod-983274")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours access token
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30         # 30 days persistent refresh token
    
    # Redis configuration with graceful in-memory fallback
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # CORS
    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "*"
    ]

settings = Settings()
