# Main register
from db.db_operations import insert_document, find_documents
from register.email_confirm import (
    generate_confirmation_token,
    send_confirmation_mail,
)
from utils.helpers import (
    green,
    red,
    blue,
    reset,
    typing_effect,
    input_quit_handle,
    clear,
    sleep,
)
from utils.auth import (
    bcrypt_hash,
    get_system_info,
    input_masking,
    validation_input,
)


def check_user_exists(email):

    email = email.strip()
    existing_user = find_documents("users", {"email": email})
    return len(existing_user) > 0


def main_register():

    while True:
        clear()
        typing_effect(blue + "Welcome to the User Registration! 🚀 " + reset)
        print()

        name = validation_input(
            green + "Enter your first name: ", "name", min_length=3
        ).title()
        surname = validation_input(
            green + "Enter your surname: ", "surname", min_length=3
        ).title()
        phone = validation_input(green + "Enter your phone number: ", "phone")
        email = validation_input(green + "Enter your email: ", "email").lower()

        if check_user_exists(email):
            print(
                red
                + f"An account with the email '{email}' already exists. Please try again."
                + reset
            )
            response = input_quit_handle("Do you want to retry? (y/n): ").lower()
            if response == "y":
                continue
            else:
                print(red + "Returning to the main menu..." + reset)
                return
        break

    # Primary password handling
    while True:
        clear()
        while True:
            password = input_masking(green + "Enter a password (min length is 4): ")
            if len(password) < 4:
                typing_effect(
                    red + "Password must be at least 4 characters long!" + reset
                )
                continue
            confirm_pass = input_masking(green + "Confirm primary password: ")
            if password != confirm_pass:
                typing_effect(red + "Passwords do not match! Try again." + reset)
                continue
            break

        # Secondary password handling
        while True:
            clear()
            sec_password = input_masking(
                green + "Enter a secondary password (min length is 4): "
            )
            if len(sec_password) < 4:
                typing_effect(
                    red
                    + "Secondary password must be at least 4 characters long!"
                    + reset
                )
                continue
            confirm_pass = input_masking(green + "Confirm secondary password: ")
            if sec_password != confirm_pass:
                typing_effect(
                    red + "Secondary passwords do not match! Try again." + reset
                )
                continue
            break

        if password == sec_password:
            print(
                red
                + "Primary and secondary passwords must be different. Please try again."
                + reset
            )
            response = input_quit_handle("Do you want to retry? (y/n): ").lower()
            if response == "y":
                continue
            else:
                print(red + "Returning to the main menu..." + reset)
                return
        break

    hashed_password = bcrypt_hash(password)
    hashed_sec_password = bcrypt_hash(sec_password)

    token = generate_confirmation_token(email)
    send_confirmation_mail(email, token)

    system_info = get_system_info()
    mac_addresses = system_info.get("mac_addresses", [])
    latitude = system_info.get("latitude", "Unknown")
    longitude = system_info.get("longitude", "Unknown")

    location = (
        f"{latitude}, {longitude}"
        if latitude != "Unknown" and longitude != "Unknown"
        else "Unknown"
    )

    user_data = {
        "name": name,
        "surname": surname,
        "email": email,
        "phone": phone,
        "password": hashed_password,
        "sec_password": hashed_sec_password,
        "role": "user",
        "token": token,
    }

    log_data = {
        "email": email,
        "location": location,
        "mac_address": mac_addresses,
    }

    try:
        insert_document("pending_users", user_data)
        insert_document("pending_log", log_data)
        typing_effect(
            green
            + "Registration almost done! Please check your email to confirm."
            + reset
        )
        sleep()
    except Exception as e:
        typing_effect(red + f"An error occurred during registration: {e}" + reset)
