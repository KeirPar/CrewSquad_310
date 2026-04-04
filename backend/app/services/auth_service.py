import bcrypt
from fastapi import HTTPException, status, Depends
import jwt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer
from app.repositories.user_repository import user_db
from app.schemas.user import User

SECRET_KEY = "secret_crewsquad_key_make_it_longer_cuz_if_under_32_characters_it_gives_a_warning" #had to make longer, tests give warnings
ALGORITHM = "HS256"
tokenUrl = "auth/login"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=tokenUrl)

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        """Turn plain text password into Bcrypt hash"""
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(pwd_bytes, salt)
        #Return as a string so it can be stored in db
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Checks if typed password matches Bcrypt hash"""
        try:
            return bcrypt.checkpw(
                plain_password.encode('utf-8'), 
                hashed_password.encode('utf-8')
            )
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict):
        """Creates a JWT token that expires in 1 hour."""
        to_encode = data.copy()
        #Make so it expires in an hour
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
        """Decodes token and gets User object for /me profile endpoint"""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        except jwt.PyJWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        user = user_db.find_by_email(email)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return user



    @staticmethod
    def get_current_user_role(token: str):
        """Decodes current JWT to find user's role."""
        try: 
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("role")
        except jwt.PyJWTError:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Couldn't validate credentials")
        
