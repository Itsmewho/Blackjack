# Generate a secret key and store it in your .env
# Maybe make this dynamic for generating a different key every time.
import secrets

print(secrets.token_hex(32))
