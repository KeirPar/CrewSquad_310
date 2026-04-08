from fastapi import APIRouter, Depends, HTTPException, status
from app.schemas.user import User, UserRole
from app.services.auth_service import AuthService
from app.schemas.report import ReportCreate, Report, ReportStatus, ReportTargetType
from app.repositories.report_repo import report_db
from app.repositories.user_repository import user_db

# Assuming get_admin is in your admin router file
# from app.routers.admin_router import get_admin 

router = APIRouter(prefix="/reports", tags=["Reports"])

# Fallback in case you can't import get_admin directly:
def verify_admin(current_user: User = Depends(AuthService.get_current_user)):
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Only admin can access.")
    return current_user


@router.post("/")
def submit_report(
    report_data: ReportCreate, 
    current_user: User = Depends(AuthService.get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can file reports.")
    
    new_report = Report(
        id=0,
        order_id=report_data.order_id,
        target_type=report_data.target_type,
        target_id=report_data.target_id,
        reason=report_data.reason
    )
    report_db.save(new_report)
    return {"message": f"Report against {report_data.target_type} submitted successfully."}


@router.get("/queue")
def get_report_queue(admin: User = Depends(verify_admin)):
    return report_db.get_all_pending()


@router.patch("/{report_id}/handle")
def handle_report(
    report_id: int, 
    decision: ReportStatus, 
    notes: str = "", 
    admin: User = Depends(verify_admin)
):
    report = report_db.find_by_id(report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    if report.status != ReportStatus.OPEN:
        raise HTTPException(status_code=400, detail="Report has already been handled.")

    report.status = decision
    report.admin_notes = notes
    report_db.save(report)
    
    if decision == ReportStatus.VALIDATED:
        if report.target_type == ReportTargetType.DRIVER:
            driver = user_db.find_by_user_id(report.target_id)
            if driver and driver.role == UserRole.DELIVERY_DRIVER:
                driver.flags += 1
                user_db.save(driver)
                

    return {"message": f"Report handled successfully. Status marked as {decision}"}