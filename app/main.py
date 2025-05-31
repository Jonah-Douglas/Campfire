from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import auth as auth_router_module
from app.api.routes import users as user_router_module


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Code to run on startup
    print(f"Lifespan: Application '{settings.PROJECT_NAME}' is starting up...")
    print(f"Lifespan: Access OpenAPI docs at: /docs or /redoc")
    print(f"Lifespan: API will be listening on specified host and port.")
    
    # Run application
    yield

    # Code to run on shutdown
    print(f"Lifespan: Application '{settings.PROJECT_NAME}' is shutting down...")

# --- Create the FastAPI application instance ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V_STR}/openapi.json",
    description=settings.PROJECT_DESCRIPTION,
    version=settings.PROJECT_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    # --- Other useful parameters ---
    summary="Main API for Campfire Application",
    # JD TODO: put in valid creds here
    # contact={
    #     "name": "Jonah Douglas/Campfire",
    #     "url": "TODO",
    #     "email": "TODO",
    # },
    # JD TODO: Confirm this license is ok
    license_info={
        "name": "Apache 2.0",
        "url": "https://www.apache.org/licenses/LICENSE-2.0.html",
    },
)

# --- Configure CORS ---
# JD TODO: Fix this later (also update .env)
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# --- Include Routers ---
api_prefix = settings.API_V_STR

app.include_router(
    auth_router_module.router, 
    prefix=f"{api_prefix}/auth", 
    tags=["Authentication & Authorization"]
)
app.include_router(
    user_router_module.router, 
    prefix=f"{api_prefix}/users", 
    tags=["Users"]
)

# --- Root Endpoint (Optional but good for health checks or basic info) ---
@app.get("/", tags=["Root"])
async def read_root():
    """
    Root endpoint providing basic API information.
    """
    return {
        "message": f"Welcome to the {settings.PROJECT_NAME}!",
        "version": settings.PROJECT_VERSION,
        "docs_url": app.docs_url,
        "redoc_url": app.redoc_url,
        "openapi_url": app.openapi_url
    }