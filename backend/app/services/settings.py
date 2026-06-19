from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/orqestra"
    redis_url: str = "redis://localhost:6379/0"
    dashscope_api_key: str = ""
    qwen_model_operational: str = "qwen3.7-plus"
    qwen_model_executive: str = "qwen-max"
    qwen_api_base: str = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    environment: str = "development"

    @property
    def debug(self) -> bool:
        return self.environment == "development"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
