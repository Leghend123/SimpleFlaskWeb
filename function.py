from flask import (
    Flask,
    render_template,
    request,
    redirect,
    session,
    jsonify,
)
import sqlite3
import re
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt()



def validate_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


def register_user(firstname, surname, username, email, password):
    hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE email = ?", (email,))
        account = cur.fetchone()

        if account:
            return "Account already exists!"
        elif not validate_email(email):
            return "Invalid email address"
        elif not all((firstname, surname, username, email, hashed_password)):
            return "Please fill out the form completely"
        else:
            cur.execute(
                "INSERT INTO users (firstname, surname, username, email, password) VALUES (?, ?, ?, ?, ?)",
                (firstname, surname, username, email, hashed_password),
            )
            con.commit()
            return None


def login_user(username, password):
    with sqlite3.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (username,))
        account = cur.fetchone()

        if account:
            hashed_password = account[5]
            if bcrypt.check_password_hash(hashed_password, password):
                session["uname"] = username
                return None
            else:
                return "Invalid username or password"
        else:
            return "Invalid username or password"


def get_user_accounts():
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users ")
            user_accounts = cur.fetchall()
        return user_accounts
    except sqlite3.Error as e:
        print("Error fetching accounts:", e)
        return []


def delete_user_account(account_id):
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE id = ?", (account_id,))
            cur.close()
            return None  # Success
    except sqlite3.Error as e:
        print("Error deleting user account:", e)
        return "An error occurred while deleting the account"


def get_user_account_by_id(account_id):
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (account_id,))
            account = cur.fetchone()
        return account
    except sqlite3.Error as e:
        print("Error fetching user account:", e)
        return None


def update_user_account(account_id, firstname, surname, username, email):
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            query = "UPDATE users SET firstname=?, surname=?, username=?, email=? WHERE id=?"
            cur.execute(query, (firstname, surname, username, email, account_id))
            con.commit()
            cur.close()
            return None  # Success
    except sqlite3.Error as e:
        print("Error updating user account:", e)
        return "An error occurred while updating the account"