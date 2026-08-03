#================================================👻===========
# PARATRA
# By YOUR NAME HERE 👻
#========👻===================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from os import getenv
from io import BytesIO
import html
from app.helpers import *


# Create the app
app = Flask(__name__)


#===================================👻========================
# App Routes Handlers
#===========👻================================================

#-----------------------------------------------------------
# Home page - Show all notes
#-----------------------------------------------------------
# @app.get("/")
# def show_home():
#     with connect_db() as db:
#         sql = """
#             SELECT id, title, body, pinned, created
#             FROM note
#             ORDER BY pinned DESC, created DESC
#         """
#         params = ()
#         notes = db.execute(sql, params).fetchall()

#         flash("Test message")
#         flash("Test SUCCESS message", "success")
#         flash("Test INFO message", "info")
#         flash("Test WARNING message", "warning")
#         flash("Test ERROR message", "error")

#         return render_template("pages/note_list.jinja", notes=notes)

@app.get("/")
def show_home():
    return render_template("pages/home.jinja")

@app.get("/login_page")
def show_login():
    return render_template("pages/login.jinja")


@app.post("/login")
def login_user():
    username = request.form.get('username', '').strip()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = """
            SELECT id, forename, surname, passwordHash, ghostHunter
            FROM user
            WHERE username=?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash(f"Unknown user", "error")
            return redirect("/login_page")

        if not check_password_hash(user["passwordHash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/login_page")

        session["logged_in"] = True
        session["user"] = {
            "id": user["id"],
            "username": username,
            "forename": user["forename"],
            "surname":  user["surname"],
            "ghostHunter": user["ghostHunter"]
        }

        flash("Login successful", "success")
        return redirect("/")
    
@app.get("/signup_page")
def show_signup():
    return render_template("pages/signup.jinja")


# Signup 

@app.post("/signup")
def add_user():
    forename = request.form.get('forename', '').strip()
    surname  = request.form.get('surname',  '').strip()
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()
    ghostHunter = request.form.get('ghostHunter')


    with connect_db() as db:
        sql = "SELECT id FROM user WHERE username=?"
        params = (username,)
        not_user = db.execute(sql, params).fetchone()

        if  not_user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/signup_page")

        pass_hash = generate_password_hash(password)

        sql = """
            INSERT INTO user (forename, surname, username, passwordHash, ghostHunter)
            VALUES (?, ?, ?, ?, ?)
        """
        params = (forename, surname, username, pass_hash, ghostHunter)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("/login_page")
    
@app.get("/report_ghost")
def report_ghost():
    return render_template("pages/reportForm.jinja")


@app.post("/sendReport")
def add_hunt():
    location  = request.form.get('location',  '').strip()
    description = request.form.get('description', '').strip()

    with connect_db() as db:
        sql = """
            INSERT INTO reportedHunt ()
            VALUES (?, ?, ?, ?, ?)
        """
        params = (forename, surname, username, pass_hash, ghostHunter)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("/login_page")








#=======================👻====================================
# Configure the app
#======================================👻=====================
load_dotenv()
app.config.from_prefixed_env()
init_logging(app)
init_text_filters(app)
init_date_filters(app)
init_error_handlers(app)
init_database()
register_commands(app)

