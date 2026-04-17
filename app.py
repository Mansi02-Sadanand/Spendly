from flask import Flask, flash, redirect, render_template, request, session, url_for, abort
import sqlite3
from database.db import get_db, init_db, seed_db, create_user, get_user_by_email, get_user_by_id
from werkzeug.security import check_password_hash

app = Flask(__name__)
app.secret_key = "dev-secret-key-change-in-production"

# Context processor to make user info available in all templates
@app.context_processor
def inject_user():
    from database.db import get_user_by_id
    user_id = session.get("user_id")
    user = get_user_by_id(user_id) if user_id else None
    return dict(current_user=user)

# Initialize database on startup
with app.app_context():
    init_db()
    seed_db()


# ------------------------------------------------------------------ #
# Routes                                                              #
# ------------------------------------------------------------------ #

@app.route("/")
def landing():
    return render_template("landing.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    # If already logged in, redirect to landing
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validation: check required fields
        if not name or not email or not password:
            flash("All fields are required", "error")
            return render_template("register.html", error="All fields are required")

        # Validation: password length
        if len(password) < 6:
            flash("Password must be at least 6 characters", "error")
            return render_template("register.html", error="Password must be at least 6 characters")

        try:
            create_user(name, email, password)
            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered", "error")
            return render_template("register.html", error="Email already registered")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # If already logged in, redirect to landing
    if session.get("user_id"):
        return redirect(url_for("landing"))

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        # Validate required fields
        if not email or not password:
            flash("Email and password are required", "error")
            return render_template("login.html")

        # Fetch user by email
        user = get_user_by_email(email)

        # Verify credentials
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            flash("Welcome back!", "success")
            return redirect(url_for("landing"))
        else:
            flash("Invalid email or password", "error")
            return render_template("login.html")

    return render_template("login.html")


@app.route("/terms")
def terms():
    return render_template("terms.html")


@app.route("/privacy")
def privacy():
    return render_template("privacy.html")


# ------------------------------------------------------------------ #
# Placeholder routes — students will implement these                  #
# ------------------------------------------------------------------ #

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "success")
    return redirect(url_for("landing"))


@app.route("/profile")
def profile():
    return "Profile page — coming in Step 4"


@app.route("/expenses/add")
def add_expense():
    return "Add expense — coming in Step 7"


@app.route("/expenses/<int:id>/edit")
def edit_expense(id):
    return "Edit expense — coming in Step 8"


@app.route("/expenses/<int:id>/delete")
def delete_expense(id):
    return "Delete expense — coming in Step 9"


if __name__ == "__main__":
    app.run(debug=True, port=5001)
