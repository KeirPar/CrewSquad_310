import bcrypt
from fastapi import HTTPException, status
import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "secret_crewsquad_key"
ALGORITHM = "HS256"

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
    def get_current_user_role(token: str):
        """Decodes current JWT to find user's role."""
        try: 
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("role")
        except jwt.PyJWTError:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Couldn't validate credentials")
        
