from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMINS: str
    PORT: int
    HOST: str
    BASE_URL: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
