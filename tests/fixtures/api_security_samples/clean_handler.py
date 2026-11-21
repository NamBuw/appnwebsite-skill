"""Clean parameterized API handler fixture for offline security baseline testing."""

import os


def get_api_secret() -> str:
    return os.environ["APP_API_SECRET"]


def get_user_profile(cursor, user_id: str, allowed_origin: str) -> dict:
    cursor.execute(
        "SELECT id, email, role FROM users WHERE id = %s",
        (user_id,),
    )
    row = cursor.fetchone()
    return {
        "headers": {
            "Access-Control-Allow-Origin": allowed_origin,
            "Access-Control-Allow-Credentials": "true",
        },
        "user": row,
    }
