from fastapi import APIRouter, HTTPException, status
from app.schemas.user import UserCreate, User


#Using temporary database until we have one fully functional (think its me over next few days?)
router = APIRouter(prefix="/auth", tags = ["Authentication"])
temp_user_db = []

#Using router and checking if email is unique/correct or not
@router.post("/register", response_model=User, status_code=status.HTTP_201_CREATED)
def register_user(user_in: UserCreate):

    for existing_user in temp_user_db:
        if existing_user.email == user_in.email:
            raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail="Email has already been registered")
        
    #Hashing simulated password to check if works for now
    simulated_hashed_password = user_in.password + "_securely_hashed"

    #Create new User object that will be added to the database
    new_user = User(
        id = len(temp_user_db) + 1,
        name = user_in.name,
        email = user_in.email,
        phone_number = user_in.phone_number,
        password_hash = simulated_hashed_password,
        role = user_in.role
    )
    temp_user_db.append(new_user)
    return new_user

