from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
import uvicorn

from app.auth.api.routes import auth as auth_router_module
from app.core.config import settings
from app.core.logging.config_dict import LOGGING_CONFIG
from app.core.logging.logger_wrapper import firelog
from app.users.api.routes import users as user_router_module

api_prefix = settings.API_V_STR


@asynccontextmanager
async def lifespan_manager(app_instance: FastAPI) -> AsyncIterator[None]:
    # Code to run on startup
    firelog.info(
        f"Lifespan: Application '{settings.PROJECT_NAME}' v{settings.PROJECT_VERSION} is starting up..."
    )
    firelog.info("Lifespan: Loading API routers...")
    firelog.info(f"Lifespan: Auth routes registered under {api_prefix}/auth")
    firelog.info(f"Lifespan: User routes registered under {api_prefix}/users")
    firelog.info(
        f"Lifespan: Access OpenAPI docs at: {app_instance.docs_url} or {app_instance.redoc_url}"
    )
    firelog.info("Lifespan: API will be listening on specified host and port.")

    # Run Application
    yield

    # Code to run on shutdown
    firelog.info(f"Lifespan: Application '{settings.PROJECT_NAME}' is shutting down...")


# --- Create the FastAPI application instance ---
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.PROJECT_VERSION,
    description=(
        f"{settings.PROJECT_DESCRIPTION}\n\n"
        "**Authentication Note:** This API uses a phone number + OTP (One-Time Password) flow. "
        "Please see the 'BearerAuth' security scheme details (click 'Authorize') for instructions on how to obtain an access token."
    ),
    openapi_url=f"{settings.API_V_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
    summary="Main API for Campfire Application",
    contact={
        "name": settings.CONTACT_NAME,
        "url": settings.CONTACT_URL,
        "email": settings.CONTACT_EMAIL,
    },
    license_info={
        "name": "Proprietary"
        if settings.LICENSE_NAME == "Proprietary"
        else settings.LICENSE_NAME or "Apache 2.0",
        "url": settings.LICENSE_URL
        or (
            "https://www.apache.org/licenses/LICENSE-2.0.html"
            if (settings.LICENSE_NAME or "Apache 2.0") == "Apache 2.0"
            else None
        ),
    },
    lifespan=lifespan_manager,
)

# --- Configure CORS ---
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    firelog.info("CORS middleware configured.")
else:
    firelog.info("CORS not configured as BACKEND_CORS_ORIGINS is not set.")


def custom_openapi() -> dict[str, Any]:
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
        contact=app.contact,
        license_info=app.license_info,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
            "description": (
                "Authentication for this API is via a Bearer token (JWT) obtained through a phone + OTP process.\n\n"
                "**Steps to Authenticate:**\n"
                f"1. **Request OTP:** Go to the `POST {api_prefix}/auth/request-otp` endpoint (listed below). Provide your `phone_number` in the request body and execute it.\n"
                "2. **Receive OTP:** You will receive an OTP via SMS to the provided phone number.\n"
                f"3. **Login with OTP:** Go to the `POST {api_prefix}/auth/verify-otp` endpoint. Provide your `phone_number` and the received `otp_code` in the request body and execute it.\n"
                "4. **Get Token:** If successful, the response will contain an `access_token`.\n"
                "5. **Authorize Here:** Copy that `access_token` and paste it into the 'Value' field below (most UIs will prefix 'Bearer ' for you) and click 'Authorize'. You can then try out the protected endpoints."
            ),
        }
    }

    app.openapi_schema = openapi_schema
    return openapi_schema


app.openapi = custom_openapi

# --- Include Routers ---
firelog.info(f"Including Auth router with prefix: {api_prefix}/auth")
app.include_router(
    auth_router_module.router,
    prefix=f"{api_prefix}/auth",
    tags=["Authentication & Authorization"],
)

firelog.info(f"Including User router with prefix: {api_prefix}/users")
app.include_router(
    user_router_module.router, prefix=f"{api_prefix}/users", tags=["Users"]
)


# --- Root Endpoint ---
@app.get("/", tags=["Root"])
async def read_root() -> dict[str, Any]:
    """
    Root endpoint providing basic API information and links.
    """
    firelog.debug("Root endpoint '/' accessed.")
    return {
        "project_name": settings.PROJECT_NAME,
        "project_description": settings.PROJECT_DESCRIPTION,
        "version": settings.PROJECT_VERSION,
        "message": "Welcome! API is operational.",
        "documentation_urls": {
            "openapi_swagger": app.docs_url,
            "redoc": app.redoc_url,
            "openapi_json": app.openapi_url,
        },
        "contact": app.contact,
        "license": app.license_info,
    }


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",  # String reference to your FastAPI app instance
        host="0.0.0.0",  # Or settings.SERVER_HOST  # noqa: S104
        port=8000,  # Or settings.SERVER_PORT
        reload=True,  # Or settings.RELOAD_APP
        log_config=LOGGING_CONFIG,  # <<< Pass the dictionary object directly
    )
