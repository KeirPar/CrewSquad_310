from ..notification_repo import notification_db
from ..payment_repo import payment_db
from ..user_repository import user_db
from ..report_repo import report_db
class RepositoryManager:
    @staticmethod
    def reset_all_repositories():
        notification_db.notifications = []
        payment_db._payments = []
        user_db._users = []
        report_db.clear_all()
