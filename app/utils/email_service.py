from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.config import settings
from pydantic import EmailStr

class EmailService:
    def __init__(self):
        self.conf = ConnectionConfig(
            MAIL_USERNAME="resend",
            MAIL_PASSWORD=settings.resend_api_key,
            MAIL_FROM=f"noreply@{settings.mail_from}",
            MAIL_PORT=587,
            MAIL_SERVER="smtp.resend.com",
            MAIL_FROM_NAME=settings.mail_from_name,
            MAIL_STARTTLS=True,
            MAIL_SSL_TLS=False,
            USE_CREDENTIALS=True,
            VALIDATE_CERTS=True
        )
        self.fast_mail = FastMail(self.conf)

    async def send_verification_email(self, email: EmailStr, username: str, verification_token: str):
        verification_link = f"{settings.frontend_url}/verify-email?token={verification_token}"

        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                    <h2 style="color: #4F46E5;">Welcome to Anonymous Feedback!</h2>
                    <p>Hi {username},</p>
                    <p>Thank you for registering with Anonymous Feedback. Please verify your email address to activate your account.</p>
                    <p style="margin: 30px 0;">
                        <a href="{verification_link}" 
                            style="background-color: #4F46E5; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; display: inline-block;">
                            Verify Email Address
                        </a>
                    </p>
                    <p>Or copy and paste this link in your browser:</p>
                    <p style="word-break: break-all; color: #666;">{verification_link}</p>
                    <p style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; font-size: 12px;">
                        This link will expire in {settings.verification_token_expire_hours} hours.<br>
                        If you didn't create an account, please ignore this email.
                    </p>
                </div>
            </body>
        </html>
        """

        message = MessageSchema(
            subject="Verify your email address - Anonymous Feedback",
            recipients=[email],
            body=html_content,
            subtype=MessageType.html
        )

        await self.fast_mail.send_message(message)

email_service = EmailService()