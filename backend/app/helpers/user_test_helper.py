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
        login_response = self.client.post(
            "/auth/login",
            json={"email": user.email, "password": user.password}
        )

        assert login_response.status_code == 200
        self.login_token = login_response.json()["access_token"]

        #   Get Current User
        get_user_response = self.client.get("/auth/me", headers={"Authorization": f"Bearer {self.login_token}"})
        current_user: User = User(**get_user_response.json())

        return current_user

    def get_current_user(self) -> User:
        get_user_response = self.client.get("/auth/me", headers={"Authorization": f"Bearer {self.login_token}"})
        current_user: User = User(**get_user_response.json())
        return current_user