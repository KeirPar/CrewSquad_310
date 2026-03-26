from fastapi import FastAPI
from app.routers import search_router, restaurant_router, payment_router, notification_router
from app.routers import order_router, auth_router, menu_router, cart_router, user_router, driver_router, admin_router #import the routers we need in our app
from app.services.admin_service import AdminService

def create_app():
    app = FastAPI(title = "CrewSquad_310 Backend") #create our FastAPI app

    app.include_router(search_router.router) #include the search router in our app
    app.include_router(order_router.router) #include the order router in our app
    app.include_router(auth_router.router)#including authorization router in our app
    app.include_router(menu_router.router)#include menu router in our app
    app.include_router(cart_router.router)#include cart router in our app
    app.include_router(restaurant_router.router)#include restaurant router in our app
    app.include_router(payment_router.router) #include payment router in our app
    app.include_router(user_router.router)  #include user router in our app
    app.include_router(driver_router.router)    #include delivery driver router in our app
    app.include_router(notification_router.router) #include notification router in our app
    app.include_router(admin_router.router) #include admin router in our app

    AdminService.create_admins()    #   Add admin accounts to the app.

    return app

app = create_app()

@app.get("/")
def read_root(): #just getting the root endpoint to return a simple message
    return {"message": "Hello World!"}