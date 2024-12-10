# Main register
import os
import time
from datetime import datetime
from models.all_models import RegisterModel
from db.db_operations import insert_document, find_documents
from utils.helpers import green, red, blue, reset, typing_effect, input_quit_handle
from utils.auth import (
    sha256_encrypt,
    bcrypt_hash,
    get_system_info,
    store_log,
    input_masking,
    validation_field,
    validation_input,
)


def check_user_exists(email):

    email = email.strip()
    existing_user = find_documents("users", {"email": email})
    return len(existing_user) > 0


def main_register():
    print()
