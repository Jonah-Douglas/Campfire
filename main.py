from fastapi import FastAPI


campfire_api = FastAPI()


@campfire_api.get("/")
async def main():
    return {"item_data": "Hello World"}