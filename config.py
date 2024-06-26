from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    pinecone_api_key: str
    openai_apikey: str
    telegram_token: str

    class Config:
        env_file = ".env"

settings = Settings()