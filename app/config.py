from pydantic import BaseSettings


class Settings(BaseSettings):
    DISCORD_TOKEN: str
    OPENAI_API_KEY: str
    OPENAI_MODEL: str

    class Config:
        env_file = ".env"


settings = Settings()
