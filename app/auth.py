
import base64
import hashlib
import hmac
import json
import os
import secrets
import time


def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)

    password_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600_000,
    ).hex()

    return f"{salt}${password_hash}"


def verify_password(password: str, stored_hash: str) -> bool:
    try:
        salt, expected_hash = stored_hash.split("$", 1)
    except ValueError:
        return False

    actual_hash = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        salt.encode("utf-8"),
        600_000,
    ).hex()

    return hmac.compare_digest(actual_hash, expected_hash)


def _get_secret() -> str:
    secret = os.environ.get("JWT_SECRET")

    if not secret:
        raise RuntimeError(
            "Set the JWT_SECRET environment variable before using tokens."
        )

    return secret


def create_token(username: str, role: str) -> str:
    payload = {
        "username": username,
        "role": role,
        "exp": int(time.time()) + 3600,
    }

    payload_bytes = json.dumps(payload).encode("utf-8")
    encoded_payload = base64.urlsafe_b64encode(
        payload_bytes
    ).decode("utf-8").rstrip("=")

    signature = hmac.new(
        _get_secret().encode("utf-8"),
        encoded_payload.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()

    return f"{encoded_payload}.{signature}"


def verify_token(token: str) -> dict:
    try:
        encoded_payload, signature = token.split(".", 1)

        expected_signature = hmac.new(
            _get_secret().encode("utf-8"),
            encoded_payload.encode("utf-8"),
            hashlib.sha256,
        ).hexdigest()

        if not hmac.compare_digest(signature, expected_signature):
            raise ValueError("Invalid token signature")

        padding = "=" * (-len(encoded_payload) % 4)
        payload_bytes = base64.urlsafe_b64decode(
            encoded_payload + padding
        )
        payload = json.loads(payload_bytes.decode("utf-8"))

        if payload["exp"] <= int(time.time()):
            raise ValueError("Token has expired")

        if payload.get("role") not in ("user", "admin"):
            raise ValueError("Invalid token role")

        if not payload.get("username"):
            raise ValueError("Invalid token username")

        return payload

    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Invalid or expired token") from exc
