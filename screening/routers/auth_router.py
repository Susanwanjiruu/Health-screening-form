

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
from jose import jwt, JWTError

from database import get_db
from core.config import settings
from core.security import (
    PasswordService, TokenSecurityService, validate_secure_session, limiter
)
from core.email_service import EmailService
from core.audit import log_audit_event
from screening.models.user import User, UserSession
from screening.schemas.auth import (
    ActivateAccountRequest, LoginRequest, VerifyLoginOtpRequest,
    RefreshTokenRequest, ForgotPasswordRequest, ResetPasswordRequest,
    ChangePasswordRequest, TokenResponse
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/activate-account")
@limiter.limit("10/minute")
def activate_provider_account(request: Request, payload: ActivateAccountRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or user.status != "Pending":
        raise HTTPException(status_code=400, detail="No pending activation found for that email.")

    if (
        user.email_verification_code != payload.access_code
        or not user.email_verification_code_expires_at
        or datetime.utcnow() > user.email_verification_code_expires_at
    ):
        raise HTTPException(status_code=400, detail="Invalid or expired access code.")

    PasswordService.validate_password_strength(payload.new_password)

    user.password_hash = PasswordService.hash_password(payload.new_password)
    user.status = "Active"
    user.is_email_verified = True
    user.email_verification_code = None
    user.email_verification_code_expires_at = None
    db.commit()

    log_audit_event(db, actor_user_id=user.user_id, action="ACCOUNT_ACTIVATED")
    return {"message": "Account activated successfully. You can now log in."}


@router.post("/login-request")
@limiter.limit("10/minute")
def login_request(request: Request, payload: LoginRequest, db: Session = Depends(get_db)):
    """Step 1: verify credentials, dispatch a login OTP by email."""
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or user.status != "Active":
        raise HTTPException(status_code=401, detail="Access Denied or Account Inactive.")

    if not PasswordService.verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid account credentials.")

    otp = TokenSecurityService.generate_six_digit_code()
    user.login_otp_code = otp
    user.otp_expires_at = datetime.utcnow() + timedelta(minutes=settings.LOGIN_OTP_VALID_MINUTES)
    db.commit()

    EmailService.send_login_otp(user.email, otp)
    return {"message": "Credentials verified. A one-time login code has been sent to your email."}


@router.post("/login-verify-otp", response_model=TokenResponse)
@limiter.limit("10/minute")
def verify_login_otp(request: Request, payload: VerifyLoginOtpRequest, db: Session = Depends(get_db)):
    """Step 2: verify the OTP, issue session + refresh tokens."""
    user = db.query(User).filter(User.email == payload.email).first()

    if not user or user.login_otp_code != payload.otp_code or not user.otp_expires_at \
            or datetime.utcnow() > user.otp_expires_at:
        raise HTTPException(status_code=400, detail="Invalid or expired login code.")

    user.login_otp_code = None
    user.otp_expires_at = None

    token_payload = TokenSecurityService.build_token_payload(user)
    session_token = TokenSecurityService.create_session_token(token_payload)
    refresh_token = TokenSecurityService.create_refresh_token(token_payload)

    db.add(UserSession(
        user_id=user.user_id,
        refresh_token=refresh_token,
        expires_at=datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_DAYS),
    ))
    db.commit()

    log_audit_event(db, actor_user_id=user.user_id, action="LOGIN_SUCCESS")
    return TokenResponse(session_token=session_token, refresh_token=refresh_token)


@router.post("/refresh-token")
@limiter.limit("20/minute")
def refresh_session_token(request: Request, payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    try:
        token_payload = jwt.decode(payload.refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        if token_payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type.")

        db_session = db.query(UserSession).filter(
            UserSession.refresh_token == payload.refresh_token,
            UserSession.is_blacklisted == False,
            UserSession.expires_at > datetime.utcnow(),
        ).first()
        if not db_session:
            raise HTTPException(status_code=401, detail="Refresh token is invalid, expired, or blacklisted.")

        user = db.query(User).filter(User.user_id == db_session.user_id).first()
        if not user or user.status != "Active":
            db_session.is_blacklisted = True
            db.commit()
            raise HTTPException(status_code=403, detail="Access Denied: account is not active.")

        new_session_token = TokenSecurityService.create_session_token(
            TokenSecurityService.build_token_payload(user)
        )
        return {"session_token": new_session_token, "token_type": "Bearer"}

    except JWTError:
        raise HTTPException(status_code=401, detail="Access Denied: corrupted or tampered token.")


@router.post("/forgot-password")
@limiter.limit("5/minute")
def forgot_password(request: Request, payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Always returns the same message, whether or not the email exists — avoids leaking valid emails."""
    user = db.query(User).filter(User.email == payload.email).first()

    if user and user.status == "Active":
        reset_token = TokenSecurityService.generate_url_safe_token()
        user.reset_token = reset_token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=settings.RESET_TOKEN_VALID_MINUTES)
        db.commit()
        EmailService.send_password_reset_link(user.email, reset_token)

    return {"message": "If an account with that email exists, a reset link has been sent."}


@router.post("/reset-password")
@limiter.limit("10/minute")
def reset_password(request: Request, payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.reset_token == payload.token).first()

    if not user or not user.reset_token_expires_at or datetime.utcnow() > user.reset_token_expires_at:
        raise HTTPException(status_code=400, detail="Invalid or expired reset link.")

    PasswordService.validate_password_strength(payload.new_password)

    user.password_hash = PasswordService.hash_password(payload.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None

    db.query(UserSession).filter(UserSession.user_id == user.user_id).update({"is_blacklisted": True})

    db.commit()
    log_audit_event(db, actor_user_id=user.user_id, action="PASSWORD_RESET")
    return {"message": "Password has been reset successfully. Please log in with your new password."}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    db: Session = Depends(get_db),
    token_data: dict = Depends(validate_secure_session),
):
    user = db.query(User).filter(User.user_id == token_data.get("user_id")).first()
    if not user or not PasswordService.verify_password(payload.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")

    PasswordService.validate_password_strength(payload.new_password)
    user.password_hash = PasswordService.hash_password(payload.new_password)
    db.commit()

    log_audit_event(db, actor_user_id=user.user_id, action="PASSWORD_CHANGED")
    return {"message": "Password updated successfully."}


@router.post("/logout")
def logout(payload: RefreshTokenRequest, db: Session = Depends(get_db),
           token_data: dict = Depends(validate_secure_session)):
    db.query(UserSession).filter(UserSession.refresh_token == payload.refresh_token).update(
        {"is_blacklisted": True}
    )
    db.commit()
    log_audit_event(db, actor_user_id=token_data.get("user_id"), action="LOGOUT")
    return {"message": "Logged out successfully."}
