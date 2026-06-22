from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/orqestra"
    redis_url: str = "redis://localhost:6379/0"
    dashscope_api_key: str = ""
    qwen_model_operational: str = "qwen3.7-plus"
    qwen_model_executive: str = "qwen-max"
    qwen_model_flash: str = "qwen3.6-flash"
    qwen_model_max_preview: str = "qwen3.6-max-preview"
    qwen_api_base: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    environment: str = "development"
    auth_enabled: bool = False
    auth_username: str = "admin"
    auth_password: str = "orqestra"
    jwt_secret: str = "orqestra-dev-secret-change-in-production"
    cors_origins: str = ""

    @property
    def debug(self) -> bool:
        return self.environment == "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
