from backend.app.routers.total_price import get_total_price

def test_get_total_price():
    assert get_total_price(items_price=0) == 0