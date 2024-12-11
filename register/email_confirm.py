import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
from utils.helpers import red, green, reset

serializer = URLSafeTimedSerializer(os.getenv("SECRET_KEY"))


def generate_confirmation_token(email):
    return serializer.dumps(email, salt="email-confirm-salt")


def confirm_token(token, expiration=600):
    try:
        email = serializer.loads(token, salt="email-confirm-salt", max_age=expiration)
    except Exception:
        return None
    return email


def send_confirmation_mail(to_email, token):
    smtp_host = os.getenv("SMTP_HOST")
    smtp_port = os.getenv("SMTP_PORT")
    smtp_user = os.getenv("SMTP_USER")
    smtp_pass = os.getenv("SMTP_PASS")

    confirmation_url = f"http://127.0.0.1:5000/confirm/{token}"

    subject = "Confirm Your Registration"
    body = f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Thank you for registering. Please confirm your email by clicking the link below:</p>
            <a href="{confirmation_url}">Confirm Your Email</a>
            <p>This link will expire in 10 minutes.</p>
        </body>
    </html>
    """
    message = MIMEMultipart()
    message["From"] = smtp_user
    message["To"] = to_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "html"))

    try:
        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, message.as_string())
            print(green + "Confirmation email sent successfully!" + reset)
    except Exception as e:
        print(red + f"Error sending email: {e}" + reset)
