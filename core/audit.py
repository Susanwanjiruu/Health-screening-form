

from sqlalchemy.orm import Session
from screening.models.user import SecurityAuditLog


def log_audit_event(
    db: Session,
    actor_user_id: int,
    action: str,
    target_beneficiary_id: str = None,
    ip_address: str = None,
) -> None:
  
    entry = SecurityAuditLog(
        action_performed=action,
        performed_by_user_id=actor_user_id,
        target_beneficiary_id=target_beneficiary_id,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
