# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.database import mongo_lifespan
from app.config import settings
from app.middleware.credits import my_credits
from app.routers.delivery import router as delivery_router
from app.routers.user import router as user_router

debug_enabled = settings.APP_DEBUG.lower() in {"1", "true", "yes", "on"}

app = FastAPI(
    lifespan=mongo_lifespan,
    docs_url='/docs' if debug_enabled else None,
)

app.middleware('http')(my_credits)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
		"http://localhost",
		"http://localhost:3000",
		"http://localhost:5173",
		"http://127.0.0.1",
		"http://127.0.0.1:3000",
		"http://127.0.0.1:5173",
		"https://wpe.net.pe",
        'https://oscaralderete.com'
	],
    allow_credentials=True,
    allow_methods=["GET", "PUT", "PATCH"],
    allow_headers=["*"],
)

app.include_router(delivery_router)
app.include_router(user_router)

@app.get("/")
def root():
    return {"msg": "ok", "table": settings.MONGODB_DB}