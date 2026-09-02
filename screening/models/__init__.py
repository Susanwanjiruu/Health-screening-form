"""
Import every model here so that Base.metadata.create_all(bind=engine)
in main.py picks up all tables. Without this, SQLAlchemy won't know
a model exists unless something has imported it first.
"""

from screening.models.user import User, UserSession, SecurityAuditLog
from screening.models.facility import Facility
from screening.models.center import CenterProfile
from screening.models.beneficiary import Beneficiary
from screening.models.screening import (
    ScreeningSubmission,
    PhysicalAndSystemicExam,
    ImmunizationRecord,
    DevelopmentalMilestone,
)
from screening.models.referral import Referral, ReferralStatusLog, ReferralStatus
