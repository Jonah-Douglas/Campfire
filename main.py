from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


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

# campfire_api.include_router(user.router)

@campfire_api.get("/")
async def main():
    return {"item_data": "Hello World!"}