import bcrypt, requests
from utils.auth import get_system_info, sha256_encrypt
from user_login.user_menu import user_login_menu
from user_login.admin_menu import admin_login_menu
from db.db_operations import find_documents, update_documents, insert_document
from utils.helpers import (
    input_quit_handle,
    typing_effect,
    current_time,
    sleep,
    red,
    green,
    blue,
    reset,
    yellow,
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

    typing_effect(red + "No account found with the provided credentials!" + reset)
    sleep()
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

    # Fetch System Info
    system_info = get_system_info()

    # Fetch Last Login Log
    last_log = find_documents("admin_log", {"name": admin["name"]})
    last_log = last_log[-1] if last_log else {}

    # Check if last log exists
    if not last_log:
        print(yellow + "First-time login detected. Skipping system info check." + reset)

        # Log the system info for future reference
        log_login_time("admin_log", admin["name"], system_info)
        print(green + "Admin login successful! Proceeding to admin menu." + reset)
        admin_login_menu(admin)
        return

    # Normalize system info for comparison
    def normalize_system_info(info):
        """Normalize system info for comparison."""
        normalized = info.copy()
        # Sort mac_addresses
        normalized["mac_addresses"] = sorted(normalized.get("mac_addresses", []))
        # Sort drives by serial numbers
        normalized["drives"] = sorted(
            normalized.get("drives", []), key=lambda d: d.get("serial", "")
        )
        # Convert latitude and longitude to rounded floats
        normalized["latitude"] = round(float(normalized.get("latitude", "0")), 4)
        normalized["longitude"] = round(float(normalized.get("longitude", "0")), 4)
        return normalized

    normalized_system_info = normalize_system_info(system_info)
    normalized_last_log = normalize_system_info(last_log.get("system_info", {}))

    # Compare System Info
    if normalized_system_info != normalized_last_log:
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
        print(red + "Your account is locked due to failed login attempts." + reset)
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

    # System Info Check
    system_info = get_system_info()

    # 2FA Flow if system info changes and 2FA is enabled
    if user.get("2fa_method") == "email":
        # Initiate 2FA flow using Flask backend
        print(blue + "Sending 2FA code to your email..." + reset)
        try:
            response = requests.post(
                "http://127.0.0.1:5000/send-2fa", json={"email": user["email"]}
            )
            response.raise_for_status()
        except requests.RequestException as e:
            print(red + f"Error sending 2FA code: {str(e)}. Login denied." + reset)
            return

        # Retrieve the expected 2FA code
        expected_code = response.json().get("code")
        if not expected_code:
            print(red + "Failed to retrieve 2FA code from server." + reset)
            return

        # Prompt user to enter the code
        code = input("Enter the 2FA code sent to your email: ").strip()

        # Verify the 2FA code
        try:
            verification_response = requests.post(
                "http://127.0.0.1:5000/verify-2fa",
                json={"code": code, "expected_code": expected_code},
            )
            verification_response.raise_for_status()
        except requests.RequestException as e:
            typing_effect(
                red + f"2FA verification failed: {str(e)}. Login denied." + reset
            )
            sleep()
            return

        print(green + "2FA verification successful!" + reset)
    elif user.get("2fa_method") == "none":
        print(blue + "2FA is disabled for this account." + reset)
    else:
        print(blue + "System info unchanged. Skipping 2FA." + reset)

    # Log successful login
    log_login_time("user_log", user["email"], system_info)

    # Proceed to User Menu
    user_login_menu(user)


def log_login_time(log_collection, identifier, system_info):
    logs = find_documents(
        log_collection,
        {"email": identifier} if log_collection == "user_log" else {"name": identifier},
    )
    log = logs[-1] if logs else None  # Use None if no logs exist

    login_times = (
        log.get("login_times", [])[-4:] if log else []
    )  # Default to empty list if no log
    login_times.append({"time": current_time()})

    if log:
        update_documents(
            log_collection,
            (
                {"email": identifier}
                if log_collection == "user_log"
                else {"name": identifier}
            ),
            {"$set": {"login_times": login_times}},
        )
    else:
        return

    print(green + "Login time logged successfully." + reset)
