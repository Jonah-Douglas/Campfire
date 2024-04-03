from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.main import api_router


campfire_api = FastAPI(
    title="Campfire API",
    openapi_url=f"/api/v1",
)


campfire_api.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

campfire_api.include_router(api_router, prefix="/api/v1")
