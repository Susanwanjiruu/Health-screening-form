from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class AuditLogEntry(BaseModel):
    log_id: int
    action_performed: str
    performed_by_user_id: int
    target_beneficiary_id: Optional[str] = None
    ip_address: Optional[str] = None
    timestamp: datetime

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    total_count: int
    limit: int
    offset: int
    logs: List[AuditLogEntry]
