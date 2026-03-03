from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root(): #just getting the root endpoint to return a simple message
    return {"message": "Hello World!"}