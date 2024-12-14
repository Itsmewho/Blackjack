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
