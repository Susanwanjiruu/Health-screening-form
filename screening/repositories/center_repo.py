from sqlalchemy.orm import Session
from screening.models.center import CenterProfile


class CenterRepository:

    @staticmethod
    def get_profile(db: Session) -> CenterProfile:
        
        return db.query(CenterProfile).first()

    @staticmethod
    def update_profile(db: Session, **fields) -> CenterProfile:
        profile = db.query(CenterProfile).first()
        if not profile:
            return None
        for key, value in fields.items():
            if value is not None:
                setattr(profile, key, value)
        db.commit()
        db.refresh(profile)
        return profile
