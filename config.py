from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    GEMINI_API_KEY:str
    SECRET_KEY:str
    ALGORITHM:str="HS256"
    ACCESS_TOKEN_EXPIRY_DAYS:int=7

    read = SettingsConfigDict(env_file=".env",extra="ignore")

settings = Settings()