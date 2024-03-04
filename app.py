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
from function import validate_email, update_user_account, register_user, login_user, get_user_accounts, get_user_account_by_id, delete_user_account

app = Flask(__name__)
app.secret_key = "leghend123"
bcrypt = Bcrypt(app)


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
