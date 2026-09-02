from sqlalchemy.orm import Session
from screening.models.facility import Facility


class FacilityRepository:

    @staticmethod
    def get_by_id(db: Session, facility_id: int) -> Facility:
        return db.query(Facility).filter(Facility.facility_id == facility_id).first()

    @staticmethod
    def list_all(db: Session, status: str = None):
        query = db.query(Facility)
        if status:
            query = query.filter(Facility.status == status)
        return query.order_by(Facility.name).all()

    @staticmethod
    def create(db: Session, name: str, contact_info: str, registered_by_admin_id: int) -> Facility:
        facility = Facility(name=name, contact_info=contact_info, registered_by_admin_id=registered_by_admin_id)
        db.add(facility)
        db.commit()
        db.refresh(facility)
        return facility

    @staticmethod
    def update_status(db: Session, facility_id: int, status: str) -> Facility:
        facility = db.query(Facility).filter(Facility.facility_id == facility_id).first()
        if facility:
            facility.status = status
            db.commit()
            db.refresh(facility)
        return facility
