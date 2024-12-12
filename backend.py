import random, os
from flask import Flask, jsonify, request
from db.db_operations import find_documents, insert_document, delete_documents
from utils.auth import send_email
from itsdangerous import URLSafeTimedSerializer
from register.email_confirm import (
    confirm_token,
)

serializer2fa = URLSafeTimedSerializer(os.getenv("SECRET_KEY_2FA"))

app = Flask(__name__)


@app.route("/confirm/<token>", methods=["GET"])
def confirm_registration(token):
    email = confirm_token(token)
    if not email:
        return jsonify({"success": False, "message": "Invalid or expired token"}), 400

    user_data = find_documents("pending_users", {"email": email})
    if not user_data:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "No pending registration found for this email",
                }
            ),
            404,
        )

    log_data = find_documents("pending_log", {"email": email})
    if not log_data:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "No pending registration found for this email",
                }
            ),
            404,
        )

    user_data = user_data[0]
    log_data = log_data[0]
    del user_data["_id"]
    del log_data["_id"]

    # Move user data to "users" collection
    try:
        insert_document("users", user_data)
        insert_document("user_log", log_data)

        # Remove data from "pending_users" and "pending_log"
        delete_documents("pending_users", {"email": email})
        delete_documents("pending_log", {"email": email})

        print("Email confirmed! Registration complete.")
        return (
            jsonify(
                {"success": True, "message": "Email confirmed! Registration complete."}
            ),
            200,
        )
    except Exception as e:
        print(f"An error occurred during confirmation: {e}")
        return (
            jsonify(
                {"success": False, "message": "An error occurred during confirmation"}
            ),
            500,
        )


@app.route("/confirm/2fa/<token>", methods=["GET"])
def confirm_2fa_email(token):
    try:
        email = confirm_token(token)
        return jsonify({"success": True, "message": "Email confirmed!", "email": email})
    except Exception:
        return jsonify({"success": False, "message": "Invalid or expired token"}), 400


@app.route("/generate-token", methods=["POST"])
def generate_token():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    token = serializer2fa.dumps(email, salt="email-confirm-salt")
    return jsonify({"success": True, "token": token})


@app.route("/send-2fa", methods=["POST"])
def send_2fa():
    data = request.json
    email = data.get("email")
    if not email:
        return jsonify({"success": False, "message": "Email is required"}), 400

    code = random.randint(100000, 999999)
    try:
        # Send the 2FA code via email
        send_email(
            to_email=email,
            subject="Your 2FA Code",
            body=f"Your 2FA code is {code}. Please enter it to complete the login process.",
        )
        return jsonify(
            {"success": True, "message": "2FA code sent successfully", "code": code}
        )
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@app.route("/verify-2fa", methods=["POST"])
def verify_2fa():
    data = request.json
    code = data.get("code")
    expected_code = data.get("expected_code")

    if not code or not expected_code:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "Both code and expected_code are required",
                }
            ),
            400,
        )

    if str(code) == str(expected_code):
        return jsonify({"success": True, "message": "2FA code verified"})
    else:
        return jsonify({"success": False, "message": "Invalid 2FA code"}), 401


if __name__ == "__main__":
    app.run(debug=True)
