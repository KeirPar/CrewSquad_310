import jwt
from datetime import datetime, timedelta, timezone

SECRET_KEY = "secret_crewsquad_key"
ALGORITHM = "HS256"

class AuthService:
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
    def verify_password(plain_password: str, hashed_password: str):
        """
        Simulated check. Will update later for real hashing real hashing.
        """
        return hashed_password == plain_password + "_fake_hash"
    
    @staticmethod
    def get_current_user_role(token: str):
        """Decodes current JWT to find user's role."""
        try: 
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload.get("role")
        except jwt.PyJWTError:
            raise HTTPException(status_code = status.HTTP_401_UNAUTHORIZED, detail = "Couldn't validate credentials")
        
        