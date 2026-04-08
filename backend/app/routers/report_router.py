from fastapi import APIRouter, Depends, HTTPException, status
from app.services import report_service
from app.schemas.user import User, UserRole
from app.services.auth_service import AuthService
from app.schemas.report import ReportCreate, Report, ReportStatus, ReportTargetType
from app.repositories.report_repo import report_db
from app.repositories.user_repository import user_db
from app.routers.admin_router import get_admin 
from typing import List

router = APIRouter(prefix="/reports", tags=["Reports"]) #all of these endpoints will be under /reports

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=Report) #posting a report, gotta be customer
def submit_report(
    report_data: ReportCreate, 
    current_user: User = Depends(AuthService.get_current_user)
):
    if current_user.role != UserRole.CUSTOMER:
        raise HTTPException(status_code=403, detail="Only customers can file reports.")
    
    try:
        return report_service.create_report(report_data, current_user) #try and create order using the service
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get("/queue", response_model= List[Report]) #getting queue of reports for admin to handle, gotta be admin
def get_report_queue(admin: User = Depends(get_admin)):
    try:
        return report_service.get_pending_reports(admin)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.patch("/{report_id}/handle", response_model=Report)
def handle_report(
    report_id: int, 
    decision: ReportStatus, 
    notes: str = "", 
    admin: User = Depends(get_admin)):

    try:
        return report_service.resolve_report(report_id, decision, notes, admin) #resolve the report 
    except ValueError as e:
        error_msg = str(e).lower()
        if "not found" in error_msg:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        elif "already been handled" in error_msg:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        else:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))