from fastapi import FastAPI
from app.routers import search #import the search router

app = FastAPI(title = "CrewSquad_310 Backend") #create our FastAPI app

app.include_router(search.router) #include the search router in our app

@app.get("/")
def read_root(): #just getting the root endpoint to return a simple message
    return {"message": "Hello World!"}