

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional

from database import get_db
from core.security import require_role
from screening.schemas.audit import AuditLogEntry, AuditLogListResponse
from screening.repositories.audit_repo import AuditRepository

router = APIRouter(prefix="/audit-logs", tags=["Audit Trail (Admin only)"])


@router.get("", response_model=AuditLogListResponse)
def list_audit_logs(
    performed_by_user_id: Optional[int] = None,
    target_beneficiary_id: Optional[str] = None,
    action_contains: Optional[str] = Query(None, description="Substring match, e.g. 'LOGIN', 'REFERRAL', 'SCREENING'"),
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
    logs = AuditRepository.list_logs(
        db,
        performed_by_user_id=performed_by_user_id,
        target_beneficiary_id=target_beneficiary_id,
        action_contains=action_contains,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset,
    )
    total = AuditRepository.count_logs(
        db,
        performed_by_user_id=performed_by_user_id,
        target_beneficiary_id=target_beneficiary_id,
        action_contains=action_contains,
        start_date=start_date,
        end_date=end_date,
    )
    return AuditLogListResponse(total_count=total, limit=limit, offset=offset, logs=logs)


@router.get("/beneficiary/{beneficiary_id}", response_model=list[AuditLogEntry])
def get_beneficiary_access_history(
    beneficiary_id: str,
    db: Session = Depends(get_db),
    token_data: dict = Depends(require_role("Admin")),
):
   
    return AuditRepository.list_logs(db, target_beneficiary_id=beneficiary_id, limit=500)
