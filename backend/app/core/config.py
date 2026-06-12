from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "FogBreaker"
    DEBUG: bool = True

    DATABASE_URL: str = "sqlite:///./data/fogbreaker.db"

    DEEPSEEK_API_KEY: str = ""
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com"
    DEEPSEEK_MODEL: str = "deepseek-chat"

    OZON_CLIENT_ID: str = ""
    OZON_API_KEY: str = ""

    HTTP_PROXY: str = ""

    CHROMA_PERSIST_DIR: str = "./data/chroma"

    COLLECT_INTERVAL_MINUTES: int = 30
    ANALYSIS_BATCH_SIZE: int = 20
    DEDUP_SIMILARITY_THRESHOLD: float = 0.9

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
