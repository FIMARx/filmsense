from flask import Flask, render_template, request, url_for, redirect, flash, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, login_user, LoginManager, login_required, current_user, logout_user
from myapp import create_app
import os
import secrets

app = Flask(__name__)
app = create_app()

# 24 byte
secret_key = secrets.token_hex(24)

app.config["SECRET_KEY"] = secret_key
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///users.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db = SQLAlchemy(app)


# CREATE TABLE IN DB
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))


# SECURITY ROUTE STAFF:
login_manager = LoginManager()
login_manager.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home_page():
    return render_template("index.html", logged_in=current_user.is_authenticated)


@app.route("/register", methods=["GET", "POST"])
def register_page():
    if request.method == "POST":
        entered_email = request.form.get("email")
        search_user = User.query.filter_by(email=entered_email).first()
        if not search_user:
            new_user = User(
                email=entered_email,
                password=generate_password_hash(
                    request.form.get("password"),
                    method="pbkdf2:sha256",
                    salt_length=8),
                name=request.form.get("name")
            )
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user)
            flash("✅ Onnittelut, olet onnistunut kirjautumaan sisään!")
            return redirect(url_for("filmsense_page"))
        if search_user:
            flash("⚠️ Olet jo rekisteröitynyt tällä sähköpostilla - Kirjaudu sen sijaan sisään!")
            return redirect(url_for("login_page"))
    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login_page():
    if request.method == "POST":
        user = User.query.filter_by(email=request.form.get("email")).first()
        if not user:
            flash('❌ Käyttäjää, jolla on annettu sähköpostiosoite EI ole olemassa, kokeile toista!')
            return redirect(url_for("login_page"))
        elif not check_password_hash(pwhash=user.password, password=request.form.get("password")):
            flash('❌ Annettu salasana EI ole oikea, kokeile toista!')
            return redirect(url_for("login_page"))
        elif user is not None and check_password_hash(pwhash=user.password, password=request.form.get("password")):
            login_user(user=user)
            flash('✅ Onnittelut, olet onnistunut kirjautumaan sisään!')
            return redirect(url_for("filmsense_page"))
    return render_template("login.html")


@app.route("/filmsense")
@login_required
def filmsense_page():
    return render_template("filmsense.html", name=current_user.name, logged_in=True)


@app.route("/logout")
@login_required
def logout_page():
    logout_user()
    return redirect(url_for("home_page", logged_in=False))


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
