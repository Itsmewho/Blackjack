from register.register import main_register
from user_login.login import login
from utils.helpers import (
    green,
    red,
    blue,
    reset,
    typing_effect,
    input_quit_handle,
    clear,
    handle_quit,
    sleep,
)


def main():

    typing_effect(blue + "Welcome to Blackjack!" + reset)
    typing_effect("type: 'q' or 'quit' to quit at any time!")
    sleep()

    while True:
        clear()

        action = input_quit_handle(
            green + "Do you want to login or register? (login/register): "
        ).lower()
        clear()

        if action in ["register", "r", "reg"]:
            clear()
            main_register()
            continue

        elif action in ["login", "log", "l"]:
            clear()
            login()
            continue

        else:
            print(red + "Invalid input. Please enter 'login' or 'register'." + reset)


if __name__ == "__main__":
    main()
