from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    OPENAI_API_KEY: str = ""
    DATABASE_URL: str = "sqlite:///./corpfinai.db"
    SEC_USER_AGENT: str = "CorpFinAI hackathon@example.com"
    LOG_LEVEL: str = "INFO"

    class Config:
        env_file = ".env"


settings = Settings()
