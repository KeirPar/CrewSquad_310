from fastapi import Security, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.services.auth_service import AuthService

security = HTTPBearer()

def verify_restaurant_owner(auth: HTTPAuthorizationCredentials = Security(security)):
    """The Gatekeeper: decodes token and check if user = owner"""

    role = AuthService.get_current_user_role(auth.credentials)

    if role != "Restaurant Owner":
        raise HTTPException(status_code = status.HTTP_403_FORBIDDEN, detail= "Access denied, Must be Restaurant Owner to Modify Menu")
    
    return role