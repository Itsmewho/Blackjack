import hashlib
import bcrypt
import json
import smtplib
import requests
import platform
import subprocess
from pathlib import Path
from colorama import Style
from email.mime.text import MIMEText
import os, re, time, getpass, msvcrt
from models.all_models import RegisterModel
from db.db_operations import find_documents
from email.mime.multipart import MIMEMultipart
from pydantic import ValidationError, BaseModel
from register.email_confirm import generate_confirmation_token, confirm_token
from utils.helpers import green, red, blue, reset, input_quit_handle


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


def verify_password(user_email, password):
    user = find_documents("users", {"email": user_email})

    if user:
        user = user[0]
        hashed_password = user["password"]

        if bcrypt.checkpw(password.encode(), hashed_password.encode()):
            return True
        else:
            return False
    else:
        print(red + "User not found." + reset)
        return False


def get_system_info():
    try:
        # MAC Addresses
        mac_addresses = []
        try:
            if platform.system() == "Windows":
                # Windows: Get MAC addresses using PowerShell
                command = (
                    'powershell -Command "Get-NetAdapter | '
                    'Select-Object -ExpandProperty MacAddress"'
                )
                output = subprocess.check_output(command, shell=True).decode().strip()
                mac_addresses = [
                    mac.replace("-", ":").strip() for mac in output.splitlines() if mac
                ]
            else:
                # Linux/Mac: Get MAC addresses using ip link or ifconfig
                try:
                    output = subprocess.check_output("ip link", shell=True).decode()
                    mac_matches = re.findall(
                        r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", output
                    )
                    mac_addresses = list(set(mac_matches))
                except Exception:
                    output = subprocess.check_output("ifconfig", shell=True).decode()
                    mac_matches = re.findall(
                        r"([0-9A-Fa-f]{2}[:-]){5}[0-9A-Fa-f]{2}", output
                    )
                    mac_addresses = list(set(mac_matches))
            mac_addresses = list(filter(None, mac_addresses))  # Remove empty entries
        except Exception as e:
            print(red + f"Error fetching MAC addresses: {e}" + reset)

        # Drives (HDD/SSD Serial Numbers)
        drives = []
        try:
            if platform.system() == "Windows":
                # Windows: Get drives using WMIC
                output = subprocess.check_output(
                    "wmic diskdrive get SerialNumber,Model", shell=True
                ).decode()
                for line in output.splitlines()[1:]:
                    if line.strip():
                        model, serial = line.strip().rsplit(None, 1)
                        drives.append({"model": model, "serial": serial})
            else:
                # Linux: Get drives using lsblk
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
        motherboard_serial = "Unknown"
        try:
            if platform.system() == "Windows":
                # Windows: Get motherboard serial using WMIC
                motherboard_serial = (
                    subprocess.check_output(
                        "wmic baseboard get serialnumber", shell=True
                    )
                    .decode()
                    .split("\n")[1]
                    .strip()
                )
            else:
                # Linux: Read from system files
                motherboard_serial = (
                    subprocess.check_output(
                        "cat /sys/class/dmi/id/board_serial", shell=True
                    )
                    .decode()
                    .strip()
                )
        except Exception as e:
            print(red + f"Error fetching motherboard serial: {e}" + reset)

        # Location (Latitude and Longitude)
        latitude, longitude = "Unknown", "Unknown"
        try:
            response = requests.get("https://ipinfo.io/json", timeout=5)
            if response.status_code == 200:
                location = response.json().get("loc", "Unknown")
                if location != "Unknown":
                    latitude, longitude = location.split(",")
        except Exception as e:
            print(red + f"Error fetching location: {e}" + reset)

        # Return System Info
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


def send_email(to_email, subject, body):
    try:
        smtp_host = os.getenv("SMTP_HOST")
        smtp_port = os.getenv("SMTP_PORT")
        smtp_user = os.getenv("SMTP_USER")
        smtp_pass = os.getenv("SMTP_PASS")

        message = MIMEMultipart()
        message["From"] = smtp_user
        message["To"] = to_email
        message["Subject"] = subject
        message.attach(MIMEText(body, "html"))

        with smtplib.SMTP_SSL(smtp_host, smtp_port) as server:
            server.login(smtp_user, smtp_pass)
            server.sendmail(smtp_user, to_email, message.as_string())
            print(green + "Confirmation email sent successfully!" + reset)
    except Exception as e:
        print(red + f"Error sending email: {e}" + reset)


def email_confirmation(email):
    token = generate_confirmation_token(email)
    confirmation_link = f"http://127.0.0.1:5000/confirm/2fa/{token}"
    send_email(
        to_email=email,
        subject="Confirm Your 2FA",
        body=f"""
    <html>
        <body>
            <p>Hello,</p>
            <p>Please confirm login by clicking the link below:</p>
            <a href="{confirmation_link}">Confirm Your Email</a>
            <p>This link will expire in 10 minutes.</p>
        </body>
    </html>
    """,
    )


def verify_login(name, password):
    admin = find_documents("admin", {"name": name})
