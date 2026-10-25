
import getpass
import sqlite3

from app.auth import hash_password
from app.database import create_tables, get_connection


def main():
    create_tables()

    username = input("Enter admin username: ").strip()
    if len(username) < 3 or len(username) > 50:
        print("Username must be between 3 and 50 characters.")
        return

    password = getpass.getpass("Enter admin password (minimum 8 characters): ")
    if len(password) < 8:
        print("Password must contain at least 8 characters.")
        return

    password_hash = hash_password(password)

    try:
        with get_connection() as connection:
            connection.execute(
                """
                INSERT INTO users (username, password_hash, role)
                VALUES (?, ?, 'admin')
                """,
                (username, password_hash),
            )
        print(f"Admin account '{username}' created successfully.")
    except sqlite3.IntegrityError:
        print("That username already exists. Choose another username.")


if __name__ == "__main__":
    main()
