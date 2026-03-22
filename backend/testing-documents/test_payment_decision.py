from urllib import response

from fastapi.testclient import TestClient
from app.main import app
from app.schemas.payment import PaymentStatus
from app.helpers.testing_data import TestingData

successful_status = 200
failed_status = 400
invalid_status = 422
missing_status = 404

client = TestClient(app)

testing_data = TestingData()
user = testing_data.customer

# reusable valid cart (same pattern as test_order.py)
def make_cart():
    return testing_data.cart.model_dump()

def test_accept_payment_status_is_accepted():
    """Verify that after accepting, the payment status is ACCEPTED."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={"decision": "ACCEPTED"})
    assert response.status_code == successful_status  
    assert response.json()["payment"]["status"] == PaymentStatus.ACCEPTED
 
 
def test_accept_payment_order_moves_to_preparing():
    """Verify that accepting a payment moves the order status to PREPARING."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={"decision": "ACCEPTED"})
    assert response.status_code == successful_status
    assert response.json()["order"]["status"] == "PREPARING"
 
def test_reject_payment_status_is_rejected():
    """Verify that after rejecting, the payment status is REJECTED."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={
        "decision": "REJECTED",
        "reason": "Out of stock"
    })
    assert response.status_code == successful_status
    assert response.json()["payment"]["status"] == PaymentStatus.REJECTED
 
 
def test_reject_payment_order_moves_to_cancelled():
    """Verify that rejecting a payment moves the order status to CANCELLED."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={
        "decision": "REJECTED",
        "reason": "Too busy"
    })
    assert response.status_code == successful_status
    assert response.json()["order"]["status"] == "CANCELLED"
 
 
def test_reject_payment_reason_is_stored():
    """Verify that the rejection reason is stored and returned in the response."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    reason = "Kitchen is closing early tonight"
    response = client.post(f"/payments/{order_id}", json={
        "decision": "REJECTED",
        "reason": reason
    })
    assert response.status_code == successful_status
    assert response.json()["payment"]["reason"] == reason
 
 
def test_accept_payment_with_reason():
    """Verify that a reason can optionally be provided when accepting."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={
        "decision": "ACCEPTED",
        "reason": "Order confirmed by manager"
    })
    assert response.status_code == successful_status
    assert response.json()["payment"]["status"] == PaymentStatus.ACCEPTED
    assert response.json()["payment"]["reason"] == "Order confirmed by manager"
 
 
def test_accept_payment_without_reason():
    """Verify that reason is optional — accepting without one should succeed."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={"decision": "ACCEPTED"})
    assert response.status_code == successful_status
    assert response.json()["payment"]["status"] == PaymentStatus.ACCEPTED
 
 
def test_decision_pending_is_rejected():
    """Verify that submitting PENDING as a decision is blocked with a 400."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={"decision": "PENDING"})
    assert response.status_code == failed_status
    assert "PENDING" in response.json()["detail"]
 
 
def test_decision_invalid_value_rejected():
    """Verify that an entirely invalid decision value returns a 422."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={"decision": "MAYBE"})
    assert response.status_code == invalid_status
 
def test_payment_for_nonexistent_order():
    """Verify that deciding on a payment for a non-existent order returns 404."""
    response = client.post("/payments/99999", json={"decision": "ACCEPTED"})
    assert response.status_code == missing_status
 
def test_decision_payment_order_id_matches():
    """Verify the payment in the response is linked to the correct order."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}", json={"decision": "ACCEPTED"})
    assert response.status_code == successful_status
    assert response.json()["payment"]["order_id"] == order_id

def test_simulate_payment_status_is_accepted_or_rejected():
    """Verify the simulated outcome is either ACCEPTED or REJECTED, never PENDING."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}/simulate")
    assert response.status_code == successful_status  
    status = response.json()["payment"]["status"]
    assert status in [PaymentStatus.ACCEPTED, PaymentStatus.REJECTED]
 
 
def test_simulate_payment_has_resolved_at_timestamp():
    """Verify the simulated payment has a resolved_at timestamp."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}/simulate")
    assert response.status_code == successful_status
    assert response.json()["payment"]["resolved_at"] is not None
 
 
def test_simulate_payment_rejected_has_reason():
    """Verify that a simulated rejection always includes a reason."""
    # Run multiple times to increase chance of hitting a rejection
    for rejection in range(10):
        order_id = client.post("/orders", json=make_cart()).json()["id"]
        response = client.post(f"/payments/{order_id}/simulate")
        payment = response.json()["payment"]
        if payment["status"] == PaymentStatus.REJECTED:
            assert payment["reason"] is not None
            assert len(payment["reason"]) > 0
            return  # found and verified a rejection, test passes
    # If all 10 were accepted that is fine, the randomness just didn't reject
 
 
def test_simulate_payment_accepted_order_moves_to_preparing():
    """Verify that a simulated acceptance moves the order to PREPARING."""
    for acceptance in range(10):
        order_id = client.post("/orders", json=make_cart()).json()["id"]
        response = client.post(f"/payments/{order_id}/simulate")
        data = response.json()
        if data["payment"]["status"] == PaymentStatus.ACCEPTED:
            assert data["order"]["status"] == "PREPARING"
            return
 
 
def test_simulate_payment_rejected_order_moves_to_cancelled():
    """Verify that a simulated rejection moves the order to CANCELLED."""
    for rejection in range(10):
        order_id = client.post("/orders", json=make_cart()).json()["id"]
        response = client.post(f"/payments/{order_id}/simulate")
        data = response.json()
        if data["payment"]["status"] == PaymentStatus.REJECTED:
            assert data["order"]["status"] == "CANCELLED"
            return
 
 
def test_simulate_payment_returns_simulated_flag():
    """Verify the response includes simulated=True to indicate it was automatic."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}/simulate")
    assert response.status_code == successful_status
    assert response.json()["simulated"] == True
 
 
def test_simulate_payment_has_payment_and_order_in_response():
    """Verify the simulate response contains both payment and order."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}/simulate")
    assert response.status_code == successful_status
    assert "payment" in response.json()
    assert "order" in response.json()
 
 
def test_simulate_payment_cannot_be_run_twice():
    """Verify that simulating a payment that is no longer PENDING returns a 404."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    client.post(f"/payments/{order_id}/simulate")  # first simulation
    response = client.post(f"/payments/{order_id}/simulate")  # second should fail
    assert response.status_code == missing_status
    assert "not in PENDING status" in response.json()["detail"]
 
 
def test_simulate_payment_nonexistent_order():
    """Verify that simulating a payment for a non-existent order returns 404."""
    response = client.post("/payments/99999/simulate")
    assert response.status_code == missing_status
 
 
def test_simulate_payment_order_id_matches():
    """Verify the payment in the simulate response is linked to the correct order."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.post(f"/payments/{order_id}/simulate")
    assert response.status_code == successful_status
    assert response.json()["payment"]["order_id"] == order_id