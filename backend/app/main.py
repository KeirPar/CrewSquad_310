from fastapi import FastAPI
from app.routers import search, order_router, auth_router, menu_router, cart_router, restaurant_router #import the routers we need in our app

app = FastAPI(title = "CrewSquad_310 Backend") #create our FastAPI app

app.include_router(search.router) #include the search router in our app
app.include_router(order_router.router) #include the order router in our app
app.include_router(auth_router.router)#including authorization router in our app
app.include_router(menu_router.router)#include menu router in our app
app.include_router(cart_router.router)#include cart router in our app
app.include_router(restaurant_router.router)#include restaurant router in our app


@app.get("/")
def read_root(): #just getting the root endpoint to return a simple message
    return {"message": "Hello World!"}