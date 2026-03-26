from fastapi.testclient import TestClient
from app.main import create_app
from app.schemas.delivery_system_configuration import DeliverySystemConfiguration
from app.schemas.user import UserCreate, UserRole
from app.helpers.user_test_helper import UserTestHelper
from app.services.admin_service import AdminService
from fastapi import status
from app.repositories.helpers.repository_manager import RepositoryManager

app = create_app()
client = TestClient(app)
user_test_helper = UserTestHelper(client=client)

def test_invalid_user_role():
    user_create: UserCreate = user_test_helper.test_user_create.model_copy()
    user_create.role = UserRole.CUSTOMER
    user_test_helper.register_and_login_user(user_create)
    response = client.post("/admin/config/update", json=DeliverySystemConfiguration(delivery_fee_multiplier=2).model_dump())
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_success_change_config():
    AdminService.create_admins()
    
    new_delivery_fee_multiplier = 2
    user_test_helper.login(email=AdminService.admin_email, password=AdminService.admin_password)
    response = client.post("/admin/config/update", json=DeliverySystemConfiguration(delivery_fee_multiplier=new_delivery_fee_multiplier).model_dump())
    response_delivery_system_configuration = DeliverySystemConfiguration(**response.json())

    assert response.status_code == status.HTTP_200_OK
    assert response_delivery_system_configuration.delivery_fee_multiplier == new_delivery_fee_multiplier