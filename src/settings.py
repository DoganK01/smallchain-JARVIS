from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_ENDPOINT: str
    GMAIL_HOST_USER: str
    TIMEZONE: str
    WEATHER_API_KEY: str
    WORLDS_NEWS_API_KEY: str

    model_config = SettingsConfigDict(env_file=".env")

    #class Config:
        #env_file = ".env"  does the same thing as above


settings = Settings()