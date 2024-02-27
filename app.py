from flask import (
    Flask,
    render_template,
    url_for,
    request,
    redirect,
    session,
    jsonify,
    flash,
)
import sqlite3
import re
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.secret_key = "leghend123"
bcrypt = Bcrypt(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/register")
def register():
    return render_template("register.html")


@app.route("/register", methods=["GET", "POST"])
def details():

    if request.method == "POST":
        try:
            # retriving the data from the form................
            firstname = request.form["fname"]
            surname = request.form["sname"]
            username = request.form["uname"]
            email = request.form["email"]
            password = request.form["pass"]
            cpassword = request.form["cpass"]
            hashed_password = bcrypt.generate_password_hash(password).decode("utf-8")
            errors = []

            # insertion into the db...........................
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE email = ?", (email,))
                account = cur.fetchone()

                if account:
                    errors.append("Account already exits!")
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", email):
                    errors.append("Invalid email address")
                elif (
                    not firstname
                    or not surname
                    or not username
                    or not email
                    or not hashed_password
                ):
                    errors.append("Please fill or the form")
                elif password != cpassword:
                    errors.append("Password do not match!")

                else:
                    cur.execute(
                        "INSERT INTO users (firstname, surname, username, email,password) VALUES(?,?,?,?,?)",
                        (firstname, surname, username, email, hashed_password),
                    )
                    con.commit()
                if errors:
                    return render_template("register.html", errors=errors)
                else:
                    success_msg = "Register successfully"
                    return render_template("register.html", success_msg=success_msg)
        except:
            errors.append("Error in the insertion")
            con.close()
    return render_template("register.html")


# Login Sesion.........................
@app.route("/login", methods=["GET", "POST"])
def login():
    errors = []
    try:
        if request.method == "POST":
            username = request.form["uname"]
            password = request.form["pass"]

            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("SELECT * FROM users WHERE username = ?", (username,))
                account = cur.fetchone()

                if account:
                    hashed_password = account[5]
                    if bcrypt.check_password_hash(hashed_password, password):
                        session["uname"] = username
                        session["success_msg"] = "Login successfully"
                        return redirect("/profile")
                    else:
                        errors.append("Invalid username or password")
                else:
                    errors.append("Invalid username or password")
    except Exception as e:
        print("Error:", e)
        errors.append(
            "An error occurred while processing your request. Please try again later."
        )

    return render_template("login.html", errors=errors)


@app.route("/profile", methods=["GET", "POST"])
def profile():
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users ")
            user_account = cur.fetchall()

    except sqlite3.Error as e:
        print("Error fetching accounts:", e)
        user_account = []

    if "uname" in session:
        username = session["uname"]
        success_msg = session.pop(
            "success_msg", None
        )  # Get and remove the success message from session
        return render_template(
            "profile.html",
            username=username,
            user_account=user_account,
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
    try:
        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("SELECT * FROM users WHERE id = ?", (account_id,))
            account = cur.fetchone()
    except sqlite3.Error as e:
        print("Error fetching account:", e)
        account = None

    if account:
        return jsonify(account=account)

    else:
        return jsonify(Error="Account not found"), 404


@app.route("/update/<int:account_id>", methods=["GET", "POST"])
def update(account_id):
    if request.method == "POST":
        firstname = request.form["fname"]
        surname = request.form["sname"]
        username = request.form["uname"]
        email = request.form["email"]

        try:
            with sqlite3.connect("database.db") as con:
                cur = con.cursor()
                query = "UPDATE users SET firstname=?, surname=?, username=?, email=? WHERE id=?"
                cur.execute(query, (firstname, surname, username, email, account_id))
                con.commit()
                cur.close()
                return jsonify(success=True)  # Return success response
        except Exception as e:
            print("Error updating account details:", e)
            return jsonify(success=False, error=str(e))  # Return error response


@app.route("/delete/<int:account_id>", methods=["POST"])
def delete(account_id):
    try:

        with sqlite3.connect("database.db") as con:
            cur = con.cursor()
            cur.execute("DELETE FROM users WHERE id = ?", (account_id,))
            cur.close()
            return jsonify(success=True)  # Return success response

    except Exception as e:
        print("Error deleting account details:", e)
        return jsonify(success=False, error=str(e))


if __name__ == "__main__":
    app.run(debug=True)
