from flask import Flask, jsonify
from db.db_operations import find_documents, insert_document, delete_documents
from register.email_confirm import confirm_token

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


if __name__ == "__main__":
    app.run(debug=True)
