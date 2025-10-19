
from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./carboniq.db")
    api_title: str = os.getenv("API_TITLE", "CarbonIQ API")
    api_version: str = os.getenv("API_VERSION", "0.1.0")

settings = Settings()
