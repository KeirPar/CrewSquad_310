from fastapi.testclient import TestClient
from app.schemas.user import User, UserCreate
from app.packages.geo.coordinate import Coordinate

class UserTestHelper:
    client: TestClient
    login_token: str = ""
    test_user_create = UserCreate(
        name="Login Tester",
        email="login_test@example.com",
        phone_number="604-9722",
        password="Password123!",
        role="Customer",
        address="789 Test Ave",
        coordinate=Coordinate(23, 3)
    )

    def __init__(self, client: TestClient):
        self.client = client

    def register_and_login_user(self, user: UserCreate) -> User:
        self.client.post(
            "/auth/register",
            json=user.model_dump()
        )

        #   Trying login
        self.login(email=user.email, password=user.password)

        #   Get Current User
        get_user_response = self.client.get("/auth/me")
        current_user: User = User(**get_user_response.json())

        return current_user

    def get_current_user(self) -> User:
        get_user_response = self.client.get("/auth/me")
        current_user: User = User(**get_user_response.json())
        return current_user
    
    def login(self, email: str, password: str) -> str:
        login_response = self.client.post(
            "/auth/login",
            json={ "email": email, "password": password }
        )

        assert login_response.status_code == 200
        login_token = login_response.json()["access_token"]
        self.login_token = login_token
        self.client.headers["Authorization"] = f"Bearer {login_token}"
        
        return login_token