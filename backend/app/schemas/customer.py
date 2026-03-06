from app.schemas.user import User

class Customer(User):
    default_address: str
    # payment_methods: List[]