"""Vulnerable API handler fixture for offline security baseline testing."""

API_SECRET = "hardcoded_api_secret_9876543210"


def get_user_profile(cursor, user_id: str) -> dict:
    query = f"SELECT id, email, role FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    row = cursor.fetchone()
    return {
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Credentials": "true",
        },
        "user": row,
    }
