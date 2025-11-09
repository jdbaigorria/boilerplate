"""
Central configuration module using Pydantic Settings.
All application settings are defined here and can be configured via environment variables.
"""

from typing import List, Optional

from pydantic import EmailStr, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings with modular feature flags.
    Load configuration from environment variables with .env file support.
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # ==================== Application Settings ====================
    APP_NAME: str = "FastAPI SaaS Boilerplate"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = "A modular and production-ready SaaS boilerplate"
    DEBUG: bool = False
    ENVIRONMENT: str = Field(default="development", pattern="^(development|staging|production)$")
    API_V1_PREFIX: str = "/api/v1"

    # ==================== Security Settings ====================
    SECRET_KEY: str = Field(..., min_length=32, description="Secret key for JWT encoding")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    PASSWORD_RESET_TOKEN_EXPIRE_HOURS: int = 24
    EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS: int = 48

    # ==================== Database Configuration - Modular ====================
    USE_POSTGRES: bool = True
    USE_MONGODB: bool = False

    # PostgreSQL Settings
    POSTGRES_HOST: Optional[str] = None
    POSTGRES_PORT: int = 5432
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    POSTGRES_POOL_SIZE: int = 5
    POSTGRES_MAX_OVERFLOW: int = 10

    # MongoDB Settings
    MONGODB_URL: Optional[str] = None
    MONGODB_DB: Optional[str] = None
    MONGODB_MIN_POOL_SIZE: int = 1
    MONGODB_MAX_POOL_SIZE: int = 10

    # ==================== Authentication - Modular ====================
    ENABLE_JWT_AUTH: bool = True
    ENABLE_OAUTH_GOOGLE: bool = False
    ENABLE_OAUTH_GITHUB: bool = False

    # OAuth - Google
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    GOOGLE_REDIRECT_URI: Optional[str] = None

    # OAuth - GitHub
    GITHUB_CLIENT_ID: Optional[str] = None
    GITHUB_CLIENT_SECRET: Optional[str] = None
    GITHUB_REDIRECT_URI: Optional[str] = None

    # ==================== SaaS Features - Modular ====================
    ENABLE_MULTI_TENANCY: bool = True
    ENABLE_SUBSCRIPTIONS: bool = True
    ENABLE_INVITATIONS: bool = True
    ENABLE_BACKGROUND_TASKS: bool = False
    ENABLE_WEBHOOKS: bool = False

    # ==================== Rate Limiting ====================
    ENABLE_RATE_LIMITING: bool = True
    RATE_LIMIT_PER_MINUTE: int = 60
    RATE_LIMIT_PER_HOUR: int = 1000
    RATE_LIMIT_PER_DAY: int = 10000

    # ==================== Redis Configuration ====================
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    REDIS_DECODE_RESPONSES: bool = True

    # ==================== Email Configuration ====================
    ENABLE_EMAIL: bool = False
    SMTP_HOST: Optional[str] = None
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    SMTP_TLS: bool = True
    SMTP_SSL: bool = False
    EMAIL_FROM: Optional[EmailStr] = None
    EMAIL_FROM_NAME: Optional[str] = None

    # ==================== AI Services - Modular ====================
    ENABLE_AI_SERVICE: bool = False
    AI_PROVIDER: Optional[str] = Field(
        default=None,
        pattern="^(openai|anthropic|gemini)$" if None else None
    )

    # AI API Keys
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4-turbo-preview"
    OPENAI_MAX_TOKENS: int = 4096

    ANTHROPIC_API_KEY: Optional[str] = None
    ANTHROPIC_MODEL: str = "claude-3-sonnet-20240229"
    ANTHROPIC_MAX_TOKENS: int = 4096

    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-pro"

    # ==================== CORS Configuration ====================
    CORS_ORIGINS: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"]
    )
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: List[str] = ["*"]
    CORS_ALLOW_HEADERS: List[str] = ["*"]

    # ==================== Monitoring & Observability ====================
    ENABLE_MONITORING: bool = True
    ENABLE_PROMETHEUS: bool = False
    ENABLE_SENTRY: bool = False
    SENTRY_DSN: Optional[str] = None

    # ==================== Logging Configuration ====================
    LOG_LEVEL: str = Field(default="INFO", pattern="^(DEBUG|INFO|WARNING|ERROR|CRITICAL)$")
    LOG_FORMAT: str = "json"  # json or pretty
    LOG_FILE: Optional[str] = None

    # ==================== Stripe Integration (for Subscriptions) ====================
    STRIPE_API_KEY: Optional[str] = None
    STRIPE_WEBHOOK_SECRET: Optional[str] = None
    STRIPE_PUBLISHABLE_KEY: Optional[str] = None

    # ==================== Celery Configuration ====================
    CELERY_BROKER_URL: Optional[str] = None
    CELERY_RESULT_BACKEND: Optional[str] = None
    CELERY_TASK_ALWAYS_EAGER: bool = False  # Set to True for synchronous testing

    # ==================== File Storage ====================
    ENABLE_FILE_STORAGE: bool = False
    STORAGE_TYPE: str = "local"  # local, s3, gcs
    UPLOAD_DIR: str = "uploads"
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB

    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_S3_BUCKET: Optional[str] = None
    AWS_S3_REGION: Optional[str] = None

    # ==================== Pagination Defaults ====================
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # ==================== Security Headers ====================
    ENABLE_SECURITY_HEADERS: bool = True

    # ==================== Validators ====================
    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v: str | List[str]) -> List[str]:
        """Parse CORS origins from string or list."""
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",")]
        return v

    @field_validator("CELERY_BROKER_URL", mode="before")
    @classmethod
    def build_celery_broker_url(cls, v: Optional[str], info) -> Optional[str]:
        """Build Celery broker URL from Redis settings if not provided."""
        if v:
            return v
        # Auto-build from Redis settings if Celery is enabled
        data = info.data
        if data.get("ENABLE_BACKGROUND_TASKS"):
            redis_password = data.get("REDIS_PASSWORD", "")
            password_part = f":{redis_password}@" if redis_password else ""
            return f"redis://{password_part}{data.get('REDIS_HOST', 'localhost')}:{data.get('REDIS_PORT', 6379)}/1"
        return None

    @field_validator("CELERY_RESULT_BACKEND", mode="before")
    @classmethod
    def build_celery_result_backend(cls, v: Optional[str], info) -> Optional[str]:
        """Build Celery result backend URL from Redis settings if not provided."""
        if v:
            return v
        # Auto-build from Redis settings if Celery is enabled
        data = info.data
        if data.get("ENABLE_BACKGROUND_TASKS"):
            redis_password = data.get("REDIS_PASSWORD", "")
            password_part = f":{redis_password}@" if redis_password else ""
            return f"redis://{password_part}{data.get('REDIS_HOST', 'localhost')}:{data.get('REDIS_PORT', 6379)}/2"
        return None

    # ==================== Computed Properties ====================
    @property
    def database_url(self) -> Optional[str]:
        """Build PostgreSQL database URL."""
        if not self.USE_POSTGRES:
            return None

        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_HOST, self.POSTGRES_DB]):
            return None

        return (
            f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def sync_database_url(self) -> Optional[str]:
        """Build synchronous PostgreSQL database URL (for Alembic)."""
        if not self.USE_POSTGRES:
            return None

        if not all([self.POSTGRES_USER, self.POSTGRES_PASSWORD, self.POSTGRES_HOST, self.POSTGRES_DB]):
            return None

        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @property
    def redis_url(self) -> str:
        """Build Redis URL."""
        password_part = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else ""
        protocol = "rediss" if self.REDIS_SSL else "redis"
        return f"{protocol}://{password_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"


# Global settings instance
settings = Settings()


# Validate critical dependencies based on enabled features
def validate_settings() -> None:
    """
    Validate that required settings are present for enabled features.
    Raises ValueError if configuration is invalid.
    """
    errors = []

    # Database validation
    if settings.USE_POSTGRES:
        if not settings.database_url:
            errors.append("PostgreSQL is enabled but database credentials are missing")

    if settings.USE_MONGODB:
        if not settings.MONGODB_URL:
            errors.append("MongoDB is enabled but MONGODB_URL is missing")

    # OAuth validation
    if settings.ENABLE_OAUTH_GOOGLE:
        if not settings.GOOGLE_CLIENT_ID or not settings.GOOGLE_CLIENT_SECRET:
            errors.append("Google OAuth is enabled but credentials are missing")

    if settings.ENABLE_OAUTH_GITHUB:
        if not settings.GITHUB_CLIENT_ID or not settings.GITHUB_CLIENT_SECRET:
            errors.append("GitHub OAuth is enabled but credentials are missing")

    # Email validation
    if settings.ENABLE_EMAIL:
        if not all([settings.SMTP_HOST, settings.SMTP_USER, settings.SMTP_PASSWORD, settings.EMAIL_FROM]):
            errors.append("Email is enabled but SMTP configuration is incomplete")

    # AI validation
    if settings.ENABLE_AI_SERVICE:
        if not settings.AI_PROVIDER:
            errors.append("AI service is enabled but AI_PROVIDER is not set")
        elif settings.AI_PROVIDER == "openai" and not settings.OPENAI_API_KEY:
            errors.append("OpenAI provider is selected but OPENAI_API_KEY is missing")
        elif settings.AI_PROVIDER == "anthropic" and not settings.ANTHROPIC_API_KEY:
            errors.append("Anthropic provider is selected but ANTHROPIC_API_KEY is missing")
        elif settings.AI_PROVIDER == "gemini" and not settings.GEMINI_API_KEY:
            errors.append("Gemini provider is selected but GEMINI_API_KEY is missing")

    # Subscriptions validation
    if settings.ENABLE_SUBSCRIPTIONS:
        if not settings.STRIPE_API_KEY:
            errors.append("Subscriptions are enabled but STRIPE_API_KEY is missing")

    # Background tasks validation
    if settings.ENABLE_BACKGROUND_TASKS:
        if not settings.CELERY_BROKER_URL:
            errors.append("Background tasks are enabled but Celery broker URL could not be built")

    if errors:
        error_message = "Configuration validation failed:\n" + "\n".join(f"  - {error}" for error in errors)
        raise ValueError(error_message)


# Run validation on import if not in testing mode
import os
if os.getenv("TESTING") != "true":
    try:
        validate_settings()
    except ValueError as e:
        # In development, just warn instead of failing
        if settings.is_development:
            print(f"⚠️  Configuration Warning: {e}")
        else:
            raise
