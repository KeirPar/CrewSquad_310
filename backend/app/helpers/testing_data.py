#   I put this file inside /app folder instead of /testing-documents folder because /testing-documents has a dash in the middle, which can't be treated as a package and import by python.
from app.repositories.user_repository import user_db
from app.schemas.customer import Customer
from app.schemas.user import UserRole
from app.packages.geo.coordinate import Coordinate
from app.schemas.restaurant_manager import RestaurantManager
from app.schemas.cart import Cart
from app.schemas.menu_item import MenuItem


#   Contains data for testing.
class TestingData:
    __test__ = False

    customer: Customer
    restaurant_manager: RestaurantManager
    cart: Cart

    def __init__(self, cart_restaurant_id: int = 5):
        cart_id = 0

        customer = Customer( #example customer
            id=1,
            name="Keir P",
            password_hash="hashthingy", 
            email="fake@gmail.com",
            phone_number="604-677-6767",
            default_address="123 Fake St",
            address="123 Fake St",
            coordinate=Coordinate(6.6767, 8.6767),
            # delivery_note="This door password is 678912", #   FIXME: applying this will cause an error when running all tests, but it's fine when running test one by one
            role=UserRole.CUSTOMER,
            cart=[cart_id]
        )
        
        user_db.save(user=customer)
        self.customer = customer

        restaurant_manager = RestaurantManager(
            id=2, 
            name="Bob", 
            password_hash="hash123", 
            email="bob@restaurant.com", 
            phone_number="250-555-6767", 
            restaurant_id=1,
            address="123 Fake St",
            coordinate=Coordinate(6.6767, 8.6767),
            role=UserRole.OWNER
        )
        user_db.save(user=restaurant_manager)
        self.restaurant_manager = restaurant_manager


        cart = Cart(
            id=cart_id,
            menu_items=[
                MenuItem(
                    id = 1,
                    name = "Burger",
                    description = "A juicy burger",
                    base_price = 10,
                    percentage_discount = 0,
                    image_url = "http://example.com/burger.jpg",
                    add_ons = [],
                    is_available = True,
                    restaurant_id = cart_restaurant_id
                ),
                MenuItem(
                    id = 2,
                    name = "Fries",
                    description = "Crispy fries",
                    base_price = 5,
                    percentage_discount = 0,
                    image_url = "http://example.com/fries.jpg",
                    add_ons = [],
                    is_available = True,
                    restaurant_id = cart_restaurant_id
                )
            ]
        )
        self.cart = cart
