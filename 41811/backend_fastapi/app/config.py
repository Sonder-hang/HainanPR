from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    TEXT2SQL_BACKEND_URL: str = "http://127.0.0.1:8000"
    TEXT2SQL_API_KEY: str = ""
    DATABASE_URL: str = "mysql+pymysql://root:22013232@127.0.0.1:3306/hainan?charset=utf8mb4"
    vite_api_base_url: str = "http://127.0.0.1:8001"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


settings = Settings()
