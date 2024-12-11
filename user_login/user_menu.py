from db.db_operations import find_documents, update_documents, delete_documents
from utils.auth import validation_input, bcrypt_hash, verify_password
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
    last_login = find_documents("user_log", {"email": user})

    while True:
        clear()
        typing_effect(green + f"Welcome back, {user}")
        typing_effect(blue + f"Last login from {last_login['location']}")
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
            blackjack(user)
        elif action == "2":
            clear()
            account_details(user)
        elif action == "3":
            clear()
            change_two_fa(user)
        elif action == "4":
            clear()
            change_password(user)
        elif action == "5":
            clear()
            view_locations(user)
        elif action == "6":
            clear()
            typing_effect(green + "Logging out,.{reset}")
            clear()
            return
        elif action == "7":
            clear()
            handle_quit()
            break
        elif action == "8":
            clear()
            delete_account(user)
            handle_quit()
        else:
            print(red + "Invalid choice, please select again." + reset)
            sleep()


def account_details(user_email):
    user = find_documents("users", {"email": user_email})[0]
    while True:
        clear()
        print(green + f"Viewing details for {user['name']}..." + reset)
        print(f"Name: {user['name']}")
        print(f"Surname: {user['surname']}")
        print(f"Email: {user['email']}")
        print()

        action = input_quit_handle(
            green + f"Do you want to change the data? (yes/no)\n"
        )
        if action in {"y", "yes"}:
            clear()
            change_details(user)
        elif action in {"n", "no"}:
            clear()
            return


def change_details(user):
    typing_effect(
        blue + "Update your details. Leave blank to keep current detail" + reset
    )

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
    sleep()


def change_two_fa(user_email):
    choice = input_quit_handle(
        green + "Choose 2FA method: \n1. Email\n2. Phone\nEnter your choice: "
    )
    if choice == "1":
        update_documents(
            "users", {"email": user_email}, {"$set": {"2fa_method": "email"}}
        )
        print("2FA method set to email.")
    elif choice == "2":
        update_documents(
            "users", {"email": user_email}, {"$set": {"2fa_method": "phone"}}
        )
        print("2FA method set to phone.")
    else:
        print("Invalid choice.")


def change_password(user_email):
    password = input_quit_handle(red + "Enter old password: ")
    if verify_password(user_email, password):
        new_password = input_quit_handle(green + "Enter new password: ")
        hashed_new_password = bcrypt_hash(new_password)
        update_documents(
            "users", {"email": user_email}, {"$set": {"password": hashed_new_password}}
        )
        print("Password updated.")
    else:
        print("Incorrect old password.")


def view_locations(user_email):
    user_log = find_documents("user_log", {"email": user_email})
    if user_log:
        print("Previous login locations:")
        for log in user_log:
            print(f"Location: {log['location']}, Date: {log['date']}")
    else:
        print("No login locations found.")
    sleep()


def delete_user_and_log(user):
    delete_documents("users", {"_id": user})
    delete_documents("user_log", {"email": user})


def delete_account(user_email):
    user = find_documents("users", {"email": user_email})[0]
    clear()
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
        delete_user_and_log(user)
        typing_effect(
            green
            + f"User '{user['name']}' and their inventory deleted successfully!"
            + reset
        )
    else:
        print(blue + "Delete action cancelled." + reset)
