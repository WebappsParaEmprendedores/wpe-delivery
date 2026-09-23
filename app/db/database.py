from contextlib import asynccontextmanager
from typing import Generator, Optional

from fastapi import FastAPI, Depends
from pymongo import MongoClient
from pymongo.database import Database as PyMongoDatabase

from app.config import settings



_client: Optional[MongoClient] = None
_db: Optional[PyMongoDatabase] = None

def get_client() -> MongoClient:
    if _client is None:
        raise RuntimeError("MongoClient not initialized")
    return _client

def get_db() -> PyMongoDatabase:
    if _db is None:
        raise RuntimeError("Database not initialized")
    return _db

def mongo_db_dependency() -> Generator[PyMongoDatabase, None, None]:
    """
    Use as:
      def endpoint(db: PyMongoDatabase = Depends(mongo_db_dependency)):
          ...
    Note: pymongo is blocking; see tips below if your endpoints are async.
    """
    yield get_db()

def _connect_sync() -> None:
    global _client, _db
    if _client is None:
        _client = MongoClient(str(settings.MONGODB_URI))
        _db = _client[settings.MONGODB_DB]

def _close_sync() -> None:
    global _client, _db
    if _client is not None:
        _client.close()
        _client = None
        _db = None

@asynccontextmanager
async def mongo_lifespan(app: FastAPI):
    """
    Attach this lifespan to your FastAPI app:
      app = FastAPI(lifespan=mongo_lifespan)
    """
    # startup: create a single MongoClient for the process
    _connect_sync()
    try:
        yield
    finally:
        # shutdown: close the client
        _close_sync()