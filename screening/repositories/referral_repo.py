from sqlalchemy.orm import Session
from screening.models.referral import Referral, ReferralStatusLog, ReferralStatus


class ReferralRepository:

    @staticmethod
    def create(db: Session, record_id: int, beneficiary_id: str, facility_id: int,
               reason: str, urgency: str, is_safeguarding_case: str) -> Referral:
        referral = Referral(
            record_id=record_id,
            beneficiary_id=beneficiary_id,
            facility_id=facility_id,
            reason=reason,
            urgency=urgency,
            is_safeguarding_case=is_safeguarding_case,
        )
        db.add(referral)
        db.commit()
        db.refresh(referral)
        return referral

    @staticmethod
    def get_by_id(db: Session, referral_id: int) -> Referral:
        return db.query(Referral).filter(Referral.referral_id == referral_id).first()

    @staticmethod
    def list_open(db: Session, facility_id: int = None, status_filter: str = None):
        query = db.query(Referral)
        if facility_id is not None:
            query = query.filter(Referral.facility_id == facility_id)
        if status_filter:
            query = query.filter(Referral.status == status_filter)
        else:
            query = query.filter(Referral.status.notin_(
                [ReferralStatus.COMPLETED.value, ReferralStatus.LOST_TO_FOLLOWUP.value]
            ))
        return query.order_by(Referral.urgency.desc(), Referral.created_at.asc()).all()

    @staticmethod
    def update_status(db: Session, referral_id: int, new_status: str, updated_by_user_id: int,
                       notes: str = None, referred_to: str = None) -> Referral:
        referral = db.query(Referral).filter(Referral.referral_id == referral_id).first()
        if not referral:
            return None

        referral.status = new_status
        if referred_to:
            referral.referred_to = referred_to

        db.add(ReferralStatusLog(
            referral_id=referral.referral_id,
            updated_by_user_id=updated_by_user_id,
            status=new_status,
            notes=notes,
        ))
        db.commit()
        db.refresh(referral)
        return referral
