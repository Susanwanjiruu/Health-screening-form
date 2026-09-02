from sqlalchemy.orm import Session
from screening.models.user import User


class UserRepository:

    @staticmethod
    def get_user_by_email(db: Session, email: str) -> User:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> User:
        return db.query(User).filter(User.user_id == user_id).first()

    @staticmethod
    def list_users(db: Session, facility_id: int = None, role: str = None):
        query = db.query(User)
        if facility_id is not None:
            query = query.filter(User.facility_id == facility_id)
        if role is not None:
            query = query.filter(User.role == role)
        return query.order_by(User.name).all()

    @staticmethod
    def toggle_status(db: Session, user_id: int, target_status: str) -> User:
        user = db.query(User).filter(User.user_id == user_id).first()
        if user:
            user.status = target_status
            db.commit()
            db.refresh(user)
        return user
