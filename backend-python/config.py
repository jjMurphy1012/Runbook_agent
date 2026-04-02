from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: str = "sk-placeholder"
    langsmith_tracing: bool = True
    langsmith_api_key: str = "lsv2-placeholder"
    langsmith_project: str = "runbook-agent"

    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_db: str = "runbook_agent"
    postgres_user: str = "postgres"
    postgres_password: str = "postgres"

    redis_host: str = "localhost"
    redis_port: int = 6379

    fastapi_host: str = "0.0.0.0"
    fastapi_port: int = 8000

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        return f"redis://{self.redis_host}:{self.redis_port}/0"


settings = Settings()
