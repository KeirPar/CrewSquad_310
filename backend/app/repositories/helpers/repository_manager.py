from ..notification_repo import notification_db
from ..order_repo import order_db
from ..payment_repo import payment_db
from ..user_repository import user_db

class RepositoryManager:
    @staticmethod
    def reset_all_repositories():
        notification_db.notifications = []
        order_db._orders = []
        payment_db._payments = []
        user_db._users = []
