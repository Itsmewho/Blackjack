import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from itsdangerous import URLSafeTimedSerializer
from utils.helpers import red, green, reset
from db.db_operations import insert_document, delete_documents, find_documents


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
    smtp_host = os.getenv("SMTP_HOST", "mail.jordytromp.com")
    smtp_port = os.getenv("SMTP_PORT", 465)
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


# def confirm_registration(token):
#     email = confirm_token(token)
#     if not email:
#         print(red + "Invalid or expired token!" + reset)
#         return False

#     user_data = find_documents("pending_users", {"email": email})
#     if not user_data:
#         print(red + "No pending registration found for this email!" + reset)
#         return False

#     user_data = user_data[0]
#     del user_data["_id"]

#     log_user = find_documents("pending_log", {"email": email})
#     if log_user:
#         log_user = log_user[0]
#         del log_user["_id"]
#     else:
#         print(red + "No log data found for this email!" + reset)
#         return False

#     # Move user data to "users" collection
#     try:
#         insert_document("users", user_data)
#         insert_document("user_log", log_user)
#         delete_documents(
#             "pending_users", {"email": email}
#         )  # Clean up pending registration
#         delete_documents("pending_user_logs", {"email": email})  # Clean up pending log

#         print(green + "Email confirmed! Registration complete." + reset)
#         return True
#     except Exception as e:
#         print(red + f"An error occurred during confirmation: {e}" + reset)
#         return False
