from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserCreate, User
from app.services.auth_service import AuthService
from app.repositories.user_repository import user_db
from app.schemas.user import UserRole
from fastapi import status


#Using temporary database until we have one fully functional (think its me over next few days?)
router = APIRouter(prefix="/auth", tags = ["Authentication"])

#Using router and checking if email is unique/correct or not
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):
    if user_in.role == UserRole.ADMIN:  #   Admin users are pre-defined in `AdminService`, can't create an admin.
         raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail="You cannot create a admin user.")

    if user_db.find_by_email(user_in.email):
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Email has already been registered")
        
    #Hashing simulated password to check if works for now
    secure_hashed_password = AuthService.hash_password(user_in.password)

    #Create new User object that will be added to the database
    new_user = User(
        id = len(user_db.get_all()) + 1,
        name = user_in.name,
        email = user_in.email,
        phone_number = user_in.phone_number,
        password_hash = secure_hashed_password,
        role = user_in.role,
        address = user_in.address,
        coordinate = user_in.coordinate,
        order_history = [],
        cart = []

    )
    user_db.save(new_user)
    return new_user

#creating new login endpoint within auth router to work with auth service
@router.post("/login")
def login(login_data: dict):
    #Finding user
    user = user_db.find_by_email(login_data.get("email"))
      
    #If user doesn't exist or password doesn't match
    if not user or not AuthService.verify_password(login_data.get("password"), user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Invalid email or password"
        )

    #Generate JWT
    token = AuthService.create_access_token(
        data={"sub": user.email, "role": user.role}
    )

    return {"access_token": token, "token_type": "bearer"}

@router.get("/me", response_model = User)
def get_user_profile (user: User = Depends(AuthService.get_current_user)):
     """Returns current user profile """
     return user

@router.get("/dashboard")
def get_user_dashboard(user: User = Depends(AuthService.get_current_user)):
    """Returns a summary for the user dashboard"""
    return {
        "message": f"Welcome back, {user.name}!",
        "stats": {
            "total_orders": len(user.order_history),
            "items_in_cart": len(user.cart)
        },
        "recent_activity": "No recent orders" if not user.order_history else "View history"
    }
