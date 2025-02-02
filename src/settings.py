from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    AZURE_OPENAI_API_KEY: str
    AZURE_OPENAI_API_VERSION: str
    AZURE_OPENAI_ENDPOINT: str
    
    GMAIL_HOST_USER: str
    TIMEZONE: str
    WEATHER_API_KEY: str
    GOOGLE_CREDENTIALS_PATH: str
    GOOGLE_MAPS_API_KEY: str

    AZURE_OPENAI_TTS_ENDPOINT: str
    AZURE_OPENAI_TTS_API_KEY: str
    AZURE_OPENAI_TTS_API_VERSION: str

    AZURE_OPENAI_WHISPER_ENDPOINT: str
    AZURE_OPENAI_WHISPER_API_KEY: str
    AZURE_OPENAI_WHISPER_API_VERSION: str

    AZURE_OPENAI_GPT_API_KEY: str
    AZURE_OPENAI_GPT_API_VERSION: str
    AZURE_OPENAI_GPT_ENDPOINT: str

    model_config = SettingsConfigDict(env_file=".env")

    #class Config:
        #env_file = ".env"  does the same thing as above


settings = Settings()