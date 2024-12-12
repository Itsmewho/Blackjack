import bcrypt, requests
from utils.auth import get_system_info, sha256_encrypt
from user_login.user_menu import user_login_menu
from user_login.admin_menu import admin_login_menu
from db.db_operations import find_documents, update_documents
from utils.helpers import (
    input_quit_handle,
    typing_effect,
    current_time,
    red,
    green,
    blue,
    reset,
)
from utils.auth import send_email, input_masking


def login():
    typing_effect(green + "Welcome to Login" + reset)
    identifier = input_quit_handle("Enter your email: ").lower()
    password = input_masking("Enter your password: ")

    hashed_name = sha256_encrypt(identifier)

    # Check if the user is an admin
    admin = find_documents("admin", {"name": hashed_name})
    if admin:
        admin = admin[0]
        return admin_login_flow(admin, password)

    # Check if the user is a regular user
    user = find_documents("users", {"email": identifier})
    if user:
        user = user[0]
        return user_login_flow(user, password)

    print(red + "No account found with the provided credentials!" + reset)
    return


def admin_login_flow(admin, password):
    print(blue + "Admin Login Detected" + reset)

    # Admins have only 1 attempt
    if not bcrypt.checkpw(password.encode(), admin["password"].encode()):
        print(red + "Incorrect password! Your account is locked." + reset)
        send_email(
            admin["email"],
            "Admin Account Locked",
            "Your admin account has been locked due to failed login attempts.",
        )
        return

    # System Info Check
    system_info = get_system_info()
    last_log = find_documents("admin_log", {"name": admin["name"]})
    last_log = last_log[-1] if last_log else {}

    if system_info != last_log.get("system_info"):
        print(red + "System info mismatch! Your account is locked." + reset)
        send_email(
            admin["email"],
            "Admin Account Locked",
            "Your admin account has been locked due to suspicious login attempts.",
        )
        return

    # Log successful login
    log_login_time("admin_log", admin["name"], system_info)

    # Proceed to Admin Menu
    admin_login_menu(admin)


def user_login_flow(user, password):
    print(blue + "User Login Detected" + reset)
    login_attempts = user.get("login_attempts", 0)

    if login_attempts >= 3:
        print(
            red
            + "Your account is locked due to multiple failed login attempts."
            + reset
        )
        send_email(
            user["email"],
            "Account Locked",
            "Your account has been locked due to suspicious login attempts.",
        )
        return

    # Verify Password
    if not bcrypt.checkpw(password.encode(), user["password"].encode()):
        login_attempts += 1
        update_documents(
            "users",
            {"email": user["email"]},
            {"$set": {"login_attempts": login_attempts}},
        )
        print(
            red
            + f"Incorrect password! Attempts remaining: {3 - login_attempts}"
            + reset
        )
        return

    # Reset login attempts after successful password verification
    update_documents("users", {"email": user["email"]}, {"$set": {"login_attempts": 0}})

    # System Info Check and 2FA
    system_info = get_system_info()
    last_log = find_documents("user_log", {"email": user["email"]})
    last_log = last_log[-1] if last_log else {}

    if system_info != last_log.get("system_info") and user.get("2fa_enabled"):
        # Initiate 2FA flow using Flask backend
        print(blue + "Sending 2FA code to your email..." + reset)
        response = requests.post(
            "http://127.0.0.1:5000/send-2fa", json={"email": user["email"]}
        )
        if response.status_code != 200:
            print(
                red
                + f"Error sending 2FA code: {response.json().get('message')}"
                + reset
            )
            return

        expected_code = response.json().get("code")
        code = input("Enter the 2FA code sent to your email: ").strip()

        # Verify 2FA code
        verification_response = requests.post(
            "http://127.0.0.1:5000/verify-2fa",
            json={"code": code, "expected_code": expected_code},
        )
        if verification_response.status_code != 200:
            print(red + "2FA verification failed! Login denied." + reset)
            return

        print(green + "2FA verification successful!" + reset)

    # Log successful login
    log_login_time("user_log", user["email"], system_info)

    # Proceed to User Menu
    user_login_menu(user)


def log_login_time(log_collection, identifier, system_info):
    log = (
        find_documents(log_collection, {"email": identifier})[-1]
        if log_collection == "user_log"
        else find_documents(log_collection, {"name": identifier})[-1]
    )

    # Maintain last 5 login times
    login_times = log.get("login_times", [])[-4:] if log else []
    login_times.append({"time": current_time(), "system_info": system_info})

    update_documents(
        log_collection,
        {"email": identifier} if log_collection == "user_log" else {"name": identifier},
        {"$set": {"login_times": login_times}},
    )
    print(green + "Login time and system info logged successfully." + reset)
