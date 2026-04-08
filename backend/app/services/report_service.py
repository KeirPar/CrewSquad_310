from app.schemas.user import User, UserRole
from app.schemas.report import ReportCreate, Report, ReportStatus, ReportTargetType
from app.repositories.report_repo import report_db
from app.repositories.user_repository import user_db
from app.repositories.restaurant_repo import RestaurantRepository

def create_report(report_data: ReportCreate, current_user: User) -> Report: #creating a report, only customers can do this
    if current_user.role != UserRole.CUSTOMER:
        raise ValueError("Only customers can file reports.")
    
    new_report = Report(
        id=0,
        order_id=report_data.order_id,
        target_type=report_data.target_type,
        target_id=report_data.target_id,
        reason=report_data.reason
    )
    return report_db.save(new_report) #save it to db

def get_pending_reports(admin_user: User) -> list[Report]: #admin getting report 
    if admin_user.role != UserRole.ADMIN:
        raise ValueError("Only admin can access the report queue.")
    return report_db.get_all_pending()

def resolve_report(report_id: int, decision: ReportStatus, notes: str, admin_user: User) -> Report: 
    if admin_user.role != UserRole.ADMIN:
        raise ValueError("Only admin can handle reports.")

    report = report_db.find_by_id(report_id)
    if not report:
        raise ValueError("Report not found.")
        
    if report.status != ReportStatus.OPEN:
        raise ValueError("Report has already been handled.")

    report.status = decision #alter the reports status and add notes based on the admins decision
    report.admin_notes = notes
    report_db.save(report) #save report
    
    if decision == ReportStatus.VALIDATED: #if the report is valid

        if report.target_type == ReportTargetType.DRIVER: #for driver
            driver = user_db.find_by_user_id(report.target_id)
            if driver and driver.role == UserRole.DELIVERY_DRIVER:
                driver.flags += 1 #increase flags
                user_db.save(driver) 

        elif report.target_type == ReportTargetType.RESTAURANT: #for restaurant
            restaurant_repo = RestaurantRepository()
            restaurant = restaurant_repo.find_by_id(report.target_id)
            if restaurant:
                new_flags = restaurant.flags + 1
                update_data = {"flags": new_flags}
                
                if new_flags >= 3: 
                    update_data["is_open"] = False
                
                restaurant_repo.update_restaurant(
                    restaurant_id=restaurant.id, 
                    update_data=update_data)
    return report