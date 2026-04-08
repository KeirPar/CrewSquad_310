import pytest
from fastapi import status
from fastapi.testclient import TestClient
from app.repositories import restaurant_repo
from app.main import create_app
from app.helpers.user_test_helper import UserTestHelper
from app.schemas.user import UserRole
from app.schemas.report import ReportStatus
from app.repositories.report_repo import report_db
from app.repositories.user_repository import user_db
from app.repositories.helpers.repository_manager import RepositoryManager
from app.repositories.restaurant_repo import RestaurantRepository
from app.schemas.restaurant import Restaurant
from app.services.admin_service import AdminService
from app.routers.report_router import ReportCreate, ReportTargetType


app = create_app()
client = TestClient(app)
user_test_helper = UserTestHelper(client=client)

def setup_users(): #setting up 3 diff users (driver, customer, admin) for testing
    RepositoryManager.reset_all_repositories() #dont need to reset orders and restaurants, just reports and the other repos 
    
    customer_create = user_test_helper.test_user_create.model_copy() #cusomer
    customer_create.email = "customer@report.com"
    customer_create.role = UserRole.CUSTOMER
    customer = user_test_helper.register_and_login_user(user=customer_create)
    customer_token = user_test_helper.login_token
    
    driver_create = user_test_helper.test_user_create.model_copy() #driver
    driver_create.email = "driver@report.com"
    driver_create.role = UserRole.DELIVERY_DRIVER
    driver = user_test_helper.register_and_login_user(user=driver_create)

    AdminService.create_admins()
    user_test_helper.login(email=AdminService.admin_email, password=AdminService.admin_password)
    admin_token = user_test_helper.login_token
    
    return customer_token, admin_token, driver.id


def test_customer_can_create_report(): #test making report as a customer, should succeed and return 201
    customer_token, _, driver_id = setup_users()
    
    response = client.post("/reports/", json={
        "order_id": 1,
        "target_type": "Driver",
        "target_id": driver_id,
        "reason": "Driver dropped the food."
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    assert response.status_code == status.HTTP_201_CREATED

def test_admin_cannot_create_report():
    _, admin_token, driver_id = setup_users()
    
    response = client.post("/reports/", json={
        "order_id": 1,
        "target_type": "Driver",
        "target_id": driver_id,
        "reason": "Admins shouldn't be able to do this."
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_customer_cannot_access_queue(): #customer should not be able to access queue
    customer_token, _, _ = setup_users()
    response = client.get("/reports/queue", headers={"Authorization": f"Bearer {customer_token}"})
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_customer_cannot_handle_report(): #customer should not be able to deal with the reports
    customer_token, _, _ = setup_users()
    
    response = client.patch("/reports/1/handle", params={
        "decision": "VALIDATED",
        "notes": "Trying to bypass security"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    assert response.status_code == status.HTTP_403_FORBIDDEN


def test_admin_can_view_pending_queue(): #admin should be able to see the pending reports
    customer_token, admin_token, driver_id = setup_users()
    
    client.post("/reports/", json={ #customer makes report
        "order_id": 1, "target_type": "Driver", "target_id": driver_id, "reason": "Bad service"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    response = client.get("/reports/queue", headers={"Authorization": f"Bearer {admin_token}"}) #admin checks queue
    
    assert response.status_code == status.HTTP_200_OK #should succeed
    assert len(response.json()) == 1

def test_handled_reports_leave_queue():
    customer_token, admin_token, driver_id = setup_users()
    
    client.post("/reports/", json={ #customer makes report
        "order_id": 1, "target_type": "Driver", "target_id": driver_id, "reason": "Bad service"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    queue = client.get("/reports/queue", headers={"Authorization": f"Bearer {admin_token}"}).json() #admin checks queue
    report_id = queue[0]["id"]
    
    client.patch(f"/reports/{report_id}/handle", params={ #admin handles report
        "decision": "DISMISSED"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    queue_after = client.get("/reports/queue", headers={"Authorization": f"Bearer {admin_token}"}).json() #so now the queue should be empty
    assert len(queue_after) == 0


def test_dismissing_report_adds_no_flags():
    customer_token, admin_token, driver_id = setup_users()
    
    client.post("/reports/", json={ #make report 
        "order_id": 1, "target_type": "Driver", "target_id": driver_id, "reason": "Fake claim"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    report_id = report_db.get_all_pending()[0].id
    
    # Admin dismisses the claim
    client.patch(f"/reports/{report_id}/handle", params={
        "decision": "DISMISSED"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    # get the driver from the database and verify no strikes were added
    driver = user_db.find_by_user_id(driver_id)
    assert driver.flags == 0

def test_validating_driver_report_adds_flag():
    customer_token, admin_token, driver_id = setup_users()
    
    client.post("/reports/", json={
        "order_id": 1, "target_type": "Driver", "target_id": driver_id, "reason": "Terrible driving"
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    report_id = report_db.get_all_pending()[0].id
    
    # Admin validates the claim
    client.patch(f"/reports/{report_id}/handle", params={
        "decision": "VALIDATED"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    # Fetch the driver from the database and make sure a strike was added
    driver = user_db.find_by_user_id(driver_id)
    assert driver.flags == 1

def test_dismissing_restaurant_report_adds_no_flags():
    customer_token, admin_token, _ = setup_users()
    restaurant_repo = RestaurantRepository()
    
    target_restaurant = restaurant_repo.find_by_id(1) #get first restaurant
    
    restaurant_repo.update_restaurant(target_restaurant.id, {"flags": 0})

    client.post("/reports/", json={
        "order_id": 1, 
        "target_type": "Restaurant", 
        "target_id": target_restaurant.id, 
        "reason": "The food was completely raw."
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    report_id = report_db.get_all_pending()[0].id #get the report id
    
    client.patch(f"/reports/{report_id}/handle", params={ #admin dismisses the report
        "decision": "DISMISSED"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    #now making sure no flags were added
    updated_restaurant = restaurant_repo.find_by_id(target_restaurant.id)
    assert updated_restaurant.flags == 0


def test_validating_restaurant_report_adds_flag():
    customer_token, admin_token, _ = setup_users()
    restaurant_repo = RestaurantRepository()
    
    target_restaurant = restaurant_repo.find_by_id(1) #get first restaurant
    
    restaurant_repo.update_restaurant(target_restaurant.id, {"flags": 0})
  
    client.post("/reports/", json={
        "order_id": 1, 
        "target_type": "Restaurant", 
        "target_id": target_restaurant.id, 
        "reason": "Found a bug in my soup."
    }, headers={"Authorization": f"Bearer {customer_token}"})
    
    report_id = report_db.get_all_pending()[0].id #get report id
    
    #admin validates the report
    client.patch(f"/reports/{report_id}/handle", params={
        "decision": "VALIDATED"
    }, headers={"Authorization": f"Bearer {admin_token}"})
    
    #restaurant should now have 1 flag
    updated_restaurant = restaurant_repo.find_by_id(target_restaurant.id)
    assert updated_restaurant.flags == 1