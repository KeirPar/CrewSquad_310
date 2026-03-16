from fastapi import Security, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService
from app.schemas.user import User

security = HTTPBearer()

#Dependency set up for restaurant owner
def verify_restaurant_owner(auth: HTTPAuthorizationCredentials = Security(security)) -> User:
    """Decodes token and check if user = owner"""

    user = AuthService.get_current_user(auth.credentials)

    #Verify user exists and is correct role, then return
    if not user or user.role != "Restaurant Owner":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Access denied, Must be a Restaurant Owner to modify the menu"
        )
    return user