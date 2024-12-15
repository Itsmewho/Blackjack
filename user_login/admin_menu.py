from db.db_operations import find_documents, update_documents, delete_documents
from utils.auth import validation_input, bcrypt_hash, verify_password, input_masking
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


def admin_login_menu(admin):
    while True:
        clear()
        typing_effect(green + f"Welcome back, {admin['name']}" + reset)

        action = input_quit_handle(
            green + f"What do you want to do? \n"
            "(1) Manage_users\n"
            "(2) Account details\n"
            "(3) Change 2FA\n"
            "(4) Change Password\n"
            "(5) Logout\n"
            "(6) Exit\n"
            "Enter your choice: "
        ).strip()

        if action == "1":
            clear()
            manage_users()
        elif action == "2":
            clear()
            account_details(admin)
        elif action == "3":
            clear()
            change_two_fa(admin["email"])
        elif action == "4":
            clear()
            change_password(admin["email"])
        elif action == "5":
            typing_effect(green + "Logging out..." + reset)
            return
        elif action == "6":
            clear()
            typing_effect(green + "Goodbye! Exiting the application." + reset)
            handle_quit()
        else:
            print(red + "Invalid choice, please select again." + reset)
            sleep()


def manage_users():
    while True:
        clear()
        users = find_documents("users")
        if not users:
            typing_effect(blue + "No user found" + reset)
            return
        print(green + f"" + reset)
        for idx, user in enumerate(users, start=1):
            print(f"({idx} {user['name']} - {user['email']})")

        print(f"({len(users) + 1} Back to main menu)")

        choice = input_quit_handle("select a user or go back").strip()
        if choice.isdigit() and 1 <= (choice) <= len(users):
            manage_user_detail(user[int(choice) - 1])
        elif choice == str(len(users) + 1):
            return
        else:
            clear()
            typing_effect(red + f"Invalid choice. Please try again" + reset)


def manage_user_detail(user):
    while True:
        clear()
        print(green + f"User Details for {user['name']}:{reset}")
        print(blue + f"Name: {user['name']}")
        print(f"Email: {user['email']}{reset}")

        action = input_quit_handle(
            "(1) Modify Details\n"
            "(2) Delete User\n"
            "(3) Back to Users Menu\n"
            "Enter your choice: "
        ).strip()

        if action == "1":
            modify_user_details_inner(user)
        elif action == "2":
            delete_user(user)
        elif action == "3":
            return
        else:
            print(red + "Invalid choice. Please try again." + reset)


def modify_user_details_inner(user):
    clear()
    print(green + f"User  detail for {user['name']}" + reset)
    new_name = input_quit_handle(
        f"Enter new name (leave blank to keep '{user['name']}'): "
    ).strip()
    new_sur = input_quit_handle(
        f"Enter new surname (leave blank to keep '{user['surname']}'): "
    ).strip()
    new_email = input_quit_handle(
        f"Enter new email (leave blank to keep '{user['email']}'): "
    ).strip()
    new_phone = input_quit_handle(
        f"Enter new phone (leave blank to keep '{user['phone']}'): "
    ).strip()
    new_2fa = input_quit_handle(
        f"Change 2fa type: email or None (leave blank to keep '{user['2fa_method']}'): "
    ).strip()

    updated_user = {
        "name": new_name if new_name else user["name"],
        "surname": new_sur if new_sur else user["surname"],
        "email": new_email if new_email else user["email"],
        "phone": new_phone if new_phone else user["phone"],
        "2fa_method": new_2fa if new_2fa else user["2fa_method"],
    }

    update_documents("users", {"_id": user["_id"]}, updated_user)
    typing_effect(green + "User details updated successfully!" + reset)
    typing_effect(green + "After new login, the changes will be visible." + reset)
    sleep()


def delete_user(user_id):
    clear()
    delete_confirmation = (
        input_quit_handle(
            red
            + f"Are you sure you want to delete user '{user_id['name']}'? (yes/no): "
            + reset
        )
        .strip()
        .lower()
    )
    if delete_confirmation == "yes":
        delete_documents("users", {"_id": user_id})
        typing_effect(green + f"User '{user_id['name']}'deleted successfully!" + reset)
        return
    else:
        print(blue + "Delete action cancelled." + reset)


def account_details(admin):
    print()


def change_two_fa(admin_email):
    print()


def change_password(admin_email):
    print()
