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

app = Flask(__name__)
app.secret_key = "leghend123"
bcrypt = Bcrypt(app)


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


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        firstname = request.form["fname"]
        surname = request.form["sname"]
        username = request.form["uname"]
        email = request.form["email"]
        password = request.form["pass"]
        cpassword = request.form["cpass"]

        error = register_user(firstname, surname, username, email, password)
        if error:
            return render_template("register.html", error=error)
        else:
            success_msg = "Registered successfully"
            return render_template("register.html", success_msg=success_msg)
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["uname"]
        password = request.form["pass"]

        error = login_user(username, password)
        if error:
            return render_template("login.html", error=error)
        else:
            session["success_msg"] = "Login successful"
            return redirect("/profile")
    return render_template("login.html")


@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "uname" in session:
        username = session["uname"]
        success_msg = session.pop("success_msg", None)
        user_accounts = get_user_accounts()
        return render_template(
            "profile.html",
            username=username,
            user_accounts=user_accounts,
            success_msg=success_msg,
        )
    else:
        return redirect("/login")


@app.route("/logout")
def logout():
    session.pop("uname", None)
    return redirect("/")


@app.route("/edit/<int:account_id>", methods=["GET"])
def edit_account(account_id):
    account = get_user_account_by_id(account_id)
    if account:
        return jsonify(account=account)
    else:
        return jsonify(Error="Account not found"), 404


@app.route("/update/<int:account_id>", methods=["POST"])
def update_account(account_id):
    if request.method == "POST":
        firstname = request.form["fname"]
        surname = request.form["sname"]
        username = request.form["uname"]
        email = request.form["email"]

        error = update_user_account(account_id, firstname, surname, username, email)
        if error:
            return jsonify(success=False, error=error)
        else:
            return jsonify(success=True)


@app.route("/delete/<int:account_id>", methods=["POST"])
def delete_account(account_id):
    error = delete_user_account(account_id)
    if error:
        return jsonify(success=False, error=error)
    else:
        return jsonify(success=True)


if __name__ == "__main__":
    app.run(debug=True)
