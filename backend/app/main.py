from fastapi import FastAPI
from app.routers.total_price import router as total_price_router

app = FastAPI()

@app.get("/")
def read_root(): #just getting the root endpoint to return a simple message
    return {"message": "Hello World!"}

app.include_router(total_price_router)