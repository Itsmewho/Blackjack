import hashlib
import bcrypt
import json
import platform
import subprocess
import requests
from pathlib import Path
from colorama import Style
import os, re, time, getpass, msvcrt
from models.all_models import RegisterModel
from db.db_operations import find_documents
from pydantic import ValidationError, BaseModel
from utils.helpers import red, blue, reset, input_quit_handle


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


def sha256_encrypt(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def bcrypt_hash(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def get_system_info():
    try:
        mac_addresses = []
        try:
            if platform.system() == "Windows":
                # Use PowerShell to get MAC addresses
                command = (
                    'powershell -Command "Get-NetAdapter | '
                    'Select-Object -ExpandProperty MacAddress"'
                )
                output = subprocess.check_output(command, shell=True).decode().strip()
                mac_addresses = output.splitlines()
                mac_addresses = [
                    mac.replace("-", ":").strip() for mac in mac_addresses if mac
                ]
            else:
                # Linux/Mac logic
                output = subprocess.check_output("ip link", shell=True).decode()
                mac_matches = re.findall(
                    r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", output
                )
                mac_addresses = list(set(mac_matches))

                # Fallback to ifconfig if ip link fails
                if not mac_addresses:
                    output = subprocess.check_output("ifconfig", shell=True).decode()
                    mac_matches = re.findall(
                        r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", output
                    )
                    mac_addresses = list(set(mac_matches))
            mac_addresses = list(filter(None, mac_addresses))  # Remove empty entries
        except Exception as e:
            print(red + f"Error fetching MAC addresses: {e}" + reset)

        # HDD/SSD Serial Numbers
        drives = []
        try:
            if platform.system() == "Windows":
                output = subprocess.check_output(
                    "wmic diskdrive get SerialNumber,Model", shell=True
                ).decode()
                for line in output.splitlines()[1:]:
                    if line.strip():
                        model, serial = line.strip().rsplit(None, 1)
                        drives.append({"model": model, "serial": serial})
            else:
                output = subprocess.check_output(
                    "lsblk -o NAME,SERIAL", shell=True
                ).decode()
                for line in output.splitlines()[1:]:
                    if line.strip():
                        parts = line.split()
                        if len(parts) == 2:
                            drives.append({"model": parts[0], "serial": parts[1]})
        except Exception as e:
            print(red + f"Error fetching HDD/SSD serial numbers: {e}" + reset)

        # Motherboard Serial Number
        try:
            if platform.system() == "Windows":
                motherboard_serial = (
                    subprocess.check_output(
                        "wmic baseboard get serialnumber", shell=True
                    )
                    .decode()
                    .split("\n")[1]
                    .strip()
                )
            else:
                motherboard_serial = (
                    subprocess.check_output(
                        "cat /sys/class/dmi/id/board_serial", shell=True
                    )
                    .decode()
                    .strip()
                )
        except Exception as e:
            motherboard_serial = "Unknown"
            print(red + f"Error fetching motherboard serial: {e}" + reset)

        # Location
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            if response.status_code == 200:
                location = response.json().get("loc", "Unknown")
                if location != "Unknown":
                    latitude, longitude = location.split(",")
                else:
                    latitude = longitude = "Unknown"
            else:
                latitude = longitude = "Unknown"
        except Exception as e:
            print(red + f"Error fetching location: {e}" + reset)
            latitude = longitude = "Unknown"

        return {
            "mac_addresses": mac_addresses,
            "drives": drives,
            "motherboard_serial": motherboard_serial,
            "latitude": latitude,
            "longitude": longitude,
        }
    except Exception as e:
        print(f"Error fetching system info: {e}")
        return {
            "mac_addresses": [],
            "drives": [],
            "motherboard_serial": "Unknown",
            "latitude": "Unknown",
            "longitude": "Unknown",
        }


def encrypt_data(data: dict) -> dict:
    encrypted_data = {}
    for key, value in data.items():
        if isinstance(value, list):  # Handle lists (e.g., multiple MACs or drives)
            encrypted_data[key] = [
                hashlib.sha256(str(item).encode()).hexdigest() for item in value
            ]
        else:
            encrypted_data[key] = hashlib.sha256(str(value).encode()).hexdigest()
    return encrypted_data


def store_log(data: dict, file_path: Path):

    encrypted_data = encrypt_data(data)

    # Ensure the data directory exists
    file_path.parent.mkdir(parents=True, exist_ok=True)

    with open(file_path, "w") as file:
        json.dump(encrypted_data, file, indent=4)
    print(f"Admin log stored securely at {file_path}")


def validation_field(field_name: str, value: str, model=RegisterModel):

    if field_name not in model.model_fields:
        return blue + f"Unknown field: {field_name}{reset}"

    field_type = model.model_fields[field_name].annotation

    class TempModel(BaseModel):
        __annotations__ = {field_name: field_type}

    try:
        TempModel(**{field_name: value})
        return True
    except ValidationError as e:
        error_message = e.errors()[0]["msg"]
        return red + f"Validation error for '{field_name}': {error_message}{reset}"


def validation_input(prompt, field_name, min_length=None, model=RegisterModel):
    while True:
        user_input = input_quit_handle(prompt).strip()

        if min_length and len(user_input) < min_length:
            print(
                red
                + f"{field_name} must be at least {min_length} characters long. Please try again.{reset}"
            )
            continue

        validation = validation_field(field_name, user_input, model)
        if validation is True:
            return user_input
        else:
            input_quit_handle(red + f"Invalid: {field_name} : {validation}{reset}")


def check_user_exists(email):

    email = email.strip()
    existing_user = find_documents("users", {"email": email})
    return len(existing_user) > 0
