from sqlalchemy.orm import Session
from screening.models.beneficiary import Beneficiary
from screening.models.screening import ScreeningSubmission


class BeneficiaryRepository:

    @staticmethod
    def get_by_id(db: Session, beneficiary_id: str) -> Beneficiary:
        return db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()

    @staticmethod
    def exists(db: Session, beneficiary_id: str) -> bool:
        return db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first() is not None

    @staticmethod
    def list_beneficiaries(db: Session, facility_id: int = None, cohort_type: str = None):
        query = db.query(Beneficiary)
        if facility_id is not None:
            query = query.filter(Beneficiary.assigned_facility_id == facility_id)
        if cohort_type is not None:
            query = query.filter(Beneficiary.cohort_type == cohort_type)
        return query.order_by(Beneficiary.last_name, Beneficiary.first_name).all()

    @staticmethod
    def create(db: Session, **fields) -> Beneficiary:
        beneficiary = Beneficiary(**fields)
        db.add(beneficiary)
        db.commit()
        db.refresh(beneficiary)
        return beneficiary

    @staticmethod
    def update(db: Session, beneficiary_id: str, admin_id: int, **fields) -> Beneficiary:
        beneficiary = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
        if not beneficiary:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(beneficiary, key, value)
        beneficiary.updated_by_admin_id = admin_id
        db.commit()
        db.refresh(beneficiary)
        return beneficiary

    @staticmethod
    def log_birth(db: Session, beneficiary_id: str, birthdate, gender, admin_id: int) -> Beneficiary:
        beneficiary = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
        if not beneficiary:
            return None
        beneficiary.cohort_type = "Survival Baby"
        beneficiary.birthdate = birthdate
        if gender:
            beneficiary.gender = gender
        beneficiary.updated_by_admin_id = admin_id
        db.commit()
        db.refresh(beneficiary)
        return beneficiary

    @staticmethod
    def assign_facility(db: Session, beneficiary_id: str, facility_id: int, admin_id: int) -> Beneficiary:
        beneficiary = db.query(Beneficiary).filter(Beneficiary.beneficiary_id == beneficiary_id).first()
        if not beneficiary:
            return None
        beneficiary.assigned_facility_id = facility_id
        beneficiary.updated_by_admin_id = admin_id
        db.commit()
        db.refresh(beneficiary)
        return beneficiary

    @staticmethod
    def list_not_yet_screened(db: Session, fiscal_year: str, facility_id: int = None):
        already_screened_ids = db.query(ScreeningSubmission.beneficiary_id).filter(
            ScreeningSubmission.fiscal_year == fiscal_year
        ).subquery()

        query = db.query(Beneficiary).filter(~Beneficiary.beneficiary_id.in_(already_screened_ids))
        if facility_id is not None:
            query = query.filter(Beneficiary.assigned_facility_id == facility_id)
        return query.all()
