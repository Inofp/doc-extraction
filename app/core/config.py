from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    openai_api_key: str | None = None
    use_llm_repair: bool = True
    min_confidence_for_llm: float = 0.55
    prefer_paddleocr: bool = True
    tesseract_lang: str = "eng"
    paddle_lang: str = "en"
    mlflow_tracking_uri: str = "file:./mlruns"
    mlflow_experiment: str = "doc_extraction"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()