import os
from dotenv import load_dotenv

from pydantic import AnyUrl
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    MONGODB_URI: AnyUrl = os.environ.get('MONGODB_URI')
    MONGODB_DB: str = os.environ.get('MONGODB_DB')
    ACCESS_BEARER_TOKEN: str = os.environ.get('ACCESS_BEARER_TOKEN')
    APP_DEBUG: str = os.environ.get('APP_DEBUG')

settings = Settings()