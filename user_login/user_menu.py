from db.db_operations import find_documents, update_documents, delete_documents
from utils.auth import validation_input, bcrypt_hash, verify_password, input_masking
from game.blackjack import blackjack
from utils.helpers import (
    red,
    green,
    blue,
    reset,
    clear,
    sleep,
    input_quit_handle,
    handle_quit,
    typing_effect,
)


# Main login
def user_login_menu(user):
    last_login = find_documents("user_log", {"email": user["email"]})
    if last_login and "login_times" in last_login[-1]:
        last_login_time = last_login[-1]["login_times"][-1].get(
            "time", "Time not available"
        )
    else:
        last_login_time = "No previous login"

    while True:
        clear()
        typing_effect(green + f"Welcome back, {user['name']}" + reset)
        typing_effect(blue + f"Last login: {last_login_time}" + reset)
        print()
        action = input_quit_handle(
            green + f"What do you want to do? \n"
            "(1) Blackjack\n"
            "(2) Account details\n"
            "(3) Change 2FA\n"
            "(4) Change Password\n"
            "(5) View login locations\n"
            "(6) Logout\n"
            "(7) Exit\n"
            "(8) Delete account\n"
            "Enter your choice: "
        ).strip()

        if action == "1":
            clear()
            blackjack()
        elif action == "2":
            clear()
            account_details(user)
        elif action == "3":
            clear()
            change_two_fa(user["email"])
        elif action == "4":
            clear()
            change_password(user["email"])
        elif action == "5":
            clear()
            view_locations(user["email"])
        elif action == "6":
            clear()
            typing_effect(green + "Logging out..." + reset)
            return
        elif action == "7":
            clear()
            typing_effect(green + "Goodbye! Exiting the application." + reset)
            handle_quit()
            break
        elif action == "8":
            clear()
            delete_account(user["email"])
            handle_quit()
            break
        else:
            print(red + "Invalid choice, please select again." + reset)
            sleep()


def account_details(user):

    while True:
        clear()
        print(green + f"Viewing idetails for {user['name']}..." + reset)
        print(blue + f"Name: {user['name']}")
        print(f"Surname: {user['surname']}")
        print(f"Email: {user['email']}{reset}")
        print()

        action = input_quit_handle(
            green + f"Do you want to change the data? (yes/no)\n{reset}"
        )
        if action in {"y", "yes"}:
            clear()
            change_details(user)
        elif action in {"n", "no"}:
            clear()
            return


def change_details(user):
    typing_effect(blue + "Update your details." + reset)

    new_name = validation_input(
        green + "Enter new name: ", "name", min_length=3
    ).title()
    new_surname = validation_input(
        green + "Enter new surname: ", "surname", min_length=3
    ).title()
    new_email = validation_input(green + "Enter new email: ", "email")
    new_phone = validation_input(green + "Enter a new phone number: ", "phone").lower()

    updated_user = {
        "name": new_name if new_name else user["name"],
        "surname": new_surname if new_surname else user["surname"],
        "email": new_email if new_email else user["email"],
        "phone": new_phone if new_phone else user["phone"],
    }

    update_documents("users", {"_id": user["_id"]}, updated_user)
    typing_effect(green + "User details updated successfully!" + reset)
    typing_effect(green + "After new login, the changes will be visible." + reset)
    sleep()


def change_two_fa(user_email):
    choice = input_quit_handle(
        green + "Choose 2FA method:\n"
        "(1) Email\n"
        "(2) Disable 2FA\n"
        "(3) Return to menu\n"
        "Enter your choice: "
    )
    if choice == "1":
        update_documents(
            "users", {"email": user_email}, {"$set": {"2fa_method": "email"}}
        )
        typing_effect(green + "2FA method set to email." + reset)
    elif choice == "2":
        update_documents(
            "users", {"email": user_email}, {"$set": {"2fa_method": "none"}}
        )
        typing_effect(red + "2FA method disabled." + reset)
    elif choice == "3":
        return
    else:
        print(red + "Invalid choice. Please try again." + reset)


def change_password(user_email):
    password = input_quit_handle(red + "Enter old password: ")
    if verify_password(user_email, password):
        while True:
            new_password = input_masking(green + "Enter new password: ")
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

        hashed_new_password = bcrypt_hash(new_password)
        update_documents(
            "users",
            {"email": user_email},
            {"$set": {"password": hashed_new_password}},
        )
        print("Password updated.")
    else:
        print("Incorrect old password.")


def view_locations(user_email):
    user_logs = find_documents("user_log", {"email": user_email})
    if user_logs:
        print(green + "Previous login locations:" + reset)
        for log in user_logs:
            if "login_times" in log:
                for entry in log["login_times"]:
                    system_info = entry.get("system_info", {})
                    latitude = system_info.get("latitude", "Unknown")
                    longitude = system_info.get("longitude", "Unknown")
                    location = f"Lat: {latitude}, Lon: {longitude}"
                    time = entry.get("time", "Time not available")
                    print(f" - Location: {location}, Date: {time}")
            else:
                print(red + "No login times found in this log." + reset)
    else:
        print(red + "No login locations found." + reset)

    choice = input_quit_handle(green + "(1) Return to menu\n" "Enter your choice: ")
    if choice == "1":
        return
    else:
        print("Invalid choice.")


def delete_user_and_log(user):
    delete_documents("users", {"_id": user})
    delete_documents("user_log", {"email": user})


def delete_account(user_email):
    user = find_documents("users", {"email": user_email})[0]
    clear()
    confirm_email = (
        input_quit_handle(red + "To confirm, please re-enter your email: " + reset)
        .strip()
        .lower()
    )

    if confirm_email != user_email:
        print(red + "Email confirmation failed. Deletion aborted." + reset)
        return

    delete_confirmation = (
        input_quit_handle(
            red
            + f"Are you sure you want to delete user '{user['name']}'? (yes/no): "
            + reset
        )
        .strip()
        .lower()
    )

    if delete_confirmation == "yes":
        delete_user_and_log(user["_id"])
        typing_effect(green + f"User '{user['name']}' deleted successfully!" + reset)
    else:
        print(blue + "Delete action cancelled." + reset)
