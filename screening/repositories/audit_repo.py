from sqlalchemy.orm import Session
from datetime import datetime
from screening.models.user import SecurityAuditLog


class AuditRepository:

    @staticmethod
    def list_logs(
        db: Session,
        performed_by_user_id: int = None,
        target_beneficiary_id: str = None,
        action_contains: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100,
        offset: int = 0,
    ):
        query = db.query(SecurityAuditLog)

        if performed_by_user_id is not None:
            query = query.filter(SecurityAuditLog.performed_by_user_id == performed_by_user_id)
        if target_beneficiary_id is not None:
            query = query.filter(SecurityAuditLog.target_beneficiary_id == target_beneficiary_id)
        if action_contains is not None:
            query = query.filter(SecurityAuditLog.action_performed.ilike(f"%{action_contains}%"))
        if start_date is not None:
            query = query.filter(SecurityAuditLog.timestamp >= start_date)
        if end_date is not None:
            query = query.filter(SecurityAuditLog.timestamp <= end_date)

        return query.order_by(SecurityAuditLog.timestamp.desc()).offset(offset).limit(limit).all()

    @staticmethod
    def count_logs(
        db: Session,
        performed_by_user_id: int = None,
        target_beneficiary_id: str = None,
        action_contains: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
    ) -> int:
        query = db.query(SecurityAuditLog)

        if performed_by_user_id is not None:
            query = query.filter(SecurityAuditLog.performed_by_user_id == performed_by_user_id)
        if target_beneficiary_id is not None:
            query = query.filter(SecurityAuditLog.target_beneficiary_id == target_beneficiary_id)
        if action_contains is not None:
            query = query.filter(SecurityAuditLog.action_performed.ilike(f"%{action_contains}%"))
        if start_date is not None:
            query = query.filter(SecurityAuditLog.timestamp >= start_date)
        if end_date is not None:
            query = query.filter(SecurityAuditLog.timestamp <= end_date)

        return query.count()
