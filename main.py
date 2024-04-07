from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.main import api_router
from core.config import settings


campfire_api = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=settings.API_V_STR,
)


campfire_api.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

campfire_api.include_router(api_router, prefix="/api/v1")
