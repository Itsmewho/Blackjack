import os, time, getpass, msvcrt
from colorama import Style


def input_masking(prompt, delay=0.02, typing_effect=False, color=None):
    try:
        delay = float(delay)
    except ValueError:
        delay = 0.02

    # If color is provided.
    if color:
        prompt = color + prompt + Style.RESET_ALL
    # Print the prompt with a typing effect (if set to True.)
    if typing_effect:
        for char in prompt:
            print(char, end="", flush=True)
            time.sleep(delay)
    else:
        print(prompt, end="", flush=True)

    user_input = ""

    # For Windows input masking.
    if os.name == "nt":
        while True:
            char = msvcrt.getch()  # Get a single character from the user.

            if char == b"\r":  # Enter key pressed.
                break
            elif char == b"\x08":  # Backspace key pressed.
                if (
                    len(user_input) > 0
                ):  # Prevent prompt to be removed if backspace is pressed.
                    user_input = user_input[:-1]
                    print("\b \b", end="", flush=True)  # Remove the last character.
            else:
                user_input += char.decode("utf-8")
                print("*", end="", flush=True)

        print()

    # For Unix-based systems (Need this for windows!!!!!)
    else:
        user_input = getpass.getpass(prompt)
        print()

    # If reset color is required, append Style.RESET_ALL
    if color:
        user_input = Style.RESET_ALL + user_input

    return user_input
