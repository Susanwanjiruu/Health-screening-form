

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

from core.config import settings


class EmailService:

    @staticmethod
    def _send_via_smtp(to_email: str, subject: str, body: str) -> None:
        message = MIMEMultipart()
        message["From"] = f"{settings.SMTP_FROM_NAME} <{settings.SMTP_FROM_EMAIL}>"
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            if settings.SMTP_USERNAME:
                server.login(settings.SMTP_USERNAME, settings.SMTP_PASSWORD)
            server.sendmail(settings.SMTP_FROM_EMAIL, to_email, message.as_string())

    @staticmethod
    def send_email(to_email: str, subject: str, body: str) -> None:
        if not settings.SMTP_HOST:
        
            print(f" To: {to_email} | Subject: {subject}\n{body}\n")
            return
        EmailService._send_via_smtp(to_email, subject, body)

  

    @staticmethod
    def send_provider_access_code(to_email: str, provider_name: str, access_code: str, facility_name: str) -> None:
        subject = f"Your access code — {facility_name}"
        body = (
            f"Hello {provider_name},\n\n"
            f"You have been registered as a health provider at {facility_name}.\n"
            f"Use this one-time access code to activate your account and set your password:\n\n"
            f"  {access_code}\n\n"
            f"This code is valid for {settings.ACCESS_CODE_VALID_DAYS} days.\n"
        )
        EmailService.send_email(to_email, subject, body)

    @staticmethod
    def send_login_otp(to_email: str, otp_code: str) -> None:
        subject = "Your login verification code"
        body = (
            f"Your one-time login code is:\n\n  {otp_code}\n\n"
            f"This code expires in {settings.LOGIN_OTP_VALID_MINUTES} minutes. "
            f"If you did not request this, you can ignore this email."
        )
        EmailService.send_email(to_email, subject, body)

    @staticmethod
    def send_password_reset_link(to_email: str, reset_token: str) -> None:
        subject = "Password reset request"
        body = (
            f"A password reset was requested for this account.\n\n"
            f"Reset token (valid {settings.RESET_TOKEN_VALID_MINUTES} minutes):\n\n"
            f"  {reset_token}\n\n"
            f"If you did not request this, you can ignore this email — your password will not change."
        )
        EmailService.send_email(to_email, subject, body)
