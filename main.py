from register.register import main_register
from utils.helpers import (
    green,
    red,
    blue,
    reset,
    typing_effect,
    input_quit_handle,
    clear,
    handle_quit,
)


def main():

    typing_effect(blue + "Welcome to Blackjack!" + reset)
    typing_effect("type: 'q' or 'quit' to quit at any time!")

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
            typing_effect(red + "In construction!" + reset)
            handle_quit()

        else:
            print(red + "Invalid input. Please enter 'login' or 'register'." + reset)


if __name__ == "__main__":
    main()
