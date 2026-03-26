import pytest
from app.schemas.menu_item import MenuItem
from pydantic import ValidationError

def test_menu_item_with_invalid_price():
    with pytest.raises(ValidationError):
        MenuItem(
            id = 1,
            name = "Burger",
            description = "A juicy burger",
            base_price = -10,
            percentage_discount = 0,
            image_url = "http://example.com/burger.jpg",
            add_ons = [],
            is_available = True,
            restaurant_id = 0
        )


def test_menu_item_with_invalid_discount():
    with pytest.raises(ValidationError):
        MenuItem(
            id = 1,
            name = "Burger",
            description = "A juicy burger",
            base_price = 10,
            percentage_discount = 2,
            image_url = "http://example.com/burger.jpg",
            add_ons = [],
            is_available = True,
            restaurant_id = 0
        )

def test_valid_menu_item():
    MenuItem(
        id = 1,
        name = "Burger",
        description = "A juicy burger",
        base_price = 10,
        percentage_discount = 0.5,
        image_url = "http://example.com/burger.jpg",
        add_ons = [],
        is_available = True,
        restaurant_id = 0
    )