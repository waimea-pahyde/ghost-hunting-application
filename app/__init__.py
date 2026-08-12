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
import datetime


# Create the app
app = Flask(__name__)

# TODO
#  - signup for hunts
#  INdividual hunt page


# - see hunt ui
# - send hunt feedback 
# - fuck thats a databsase thing isn't it
#  - fit database
#  - stop at nice park benches to delay arrival at bridges to cross


















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

    with connect_db() as db:
            sql = """
            SELECT * FROM reportedHunt

            """
              # LEFT JOIN user ON reportedHunt.reportedBy = user.id
            hunts = db.execute(sql).fetchall()

            myHunts = None
            
            if session.get("user") and session.get("logged_in"):
                sql = """
                SELECT *
                FROM participant 
                JOIN reportedHunt ON participant.huntID = reportedHunt.id
                WHERE participant.ghostHunterID = ? 
                """
                params = [session["user"]["id"]]
                

                myHunts = db.execute(sql, params).fetchall()

            
            
            return render_template("pages/home.jinja", hunts=hunts, myHunts=myHunts)


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

# joining hunt 

@app.post("/join_hunt/<int:id>")
@login_required
def join_hunt(id):

# rip out the check if user exists from the signup table and put it here. 
    with connect_db() as db:
        sql = "SELECT huntID FROM participant WHERE ghostHunterID=?"
        params = [session["user"]["id"]]
        signedUp = db.execute(sql, params).fetchone()

        if  signedUp:
            flash("You have already signed up for this hunt!", "error")
            return redirect("/")
        
        
        sql = """
            INSERT INTO participant (huntID, ghostHunterID )
            VALUES (?, ?)
        """
        params = (id, session["user"]["id"])
        db.execute(sql, params)

        flash("You have signed up for this hunt.")
        return redirect("/")

@app.get("/view_hunt/<int:id>")
def view_hunt(id):
    with connect_db() as db:
        sql = """
            SELECT  
                reportedHunt.id,
                reportedHunt.reportedBy,
                reportedHunt.details,
                reportedHunt.dateReported,
                DATE(reportedHunt.dateReported, '+7 days', 'localtime') AS huntDate,
                reportedHunt.location,
                DATE('now', 'localtime') AS today
                
            FROM reportedHunt WHERE id=?
        """
        # see if there's a better way to do the date now once it works. 
        params = [id]
        hunt = db.execute(sql, params).fetchone()

    return render_template("pages/hunt.jinja", hunt=hunt)


# Hunt page. Go to see hunt. 
# Before the hunt starts:
# See location, the fellow people who are also hunting with me, when it starts, and an option to see the initial report. +Option to proceed into the hunt screen early. 
# If time: a way back to that screen while the hunt hasn't started. 

# During the hunt:
# See list of who's participating, messages, initial ghost report, end hunt button. 
# If time: current location of alll the hunters. 

#After hunt: 
# A place to summarise the hunt outcomes, a place for recdcomended next steps, a place to get photos, option to return without report. 
# Figure out how to make this work. Ideas: Allocate one member to create the hunt. Other people send photos to them, they wreite report. Hunt leader situation could be helpful
#for other things I can't remember. First in is hunt leader? Or, reports get tacked on one after another. 


# Do time stamps. Make it actually tick down. 
# Potentially go with leader scenario. Leader picks date and time. Implement leader thing later. 

@app.get("/hunting/<int:id>")
def hunt(id):
    with connect_db() as db:
        sql = """
            SELECT  * FROM reportedHunt WHERE id=?
        """
        params = [id]
        hunt = db.execute(sql, params).fetchone()

        sql = """
            SELECT  * FROM participant
            JOIN user AS hunters ON participant.ghostHunterID = hunters.id 
            WHERE participant.huntID=?
        """
        params = [id]
        participants = db.execute(sql, params).fetchall()

    return render_template("pages/hunting.jinja", hunt=hunt, participants=participants)


# in progress hunt. Merge w top once all in one

@app.get("/hunting_inhunt/<int:id>")
def in_hunt(id):
        with connect_db() as db:
            sql = """
                SELECT  * FROM participant
                JOIN user AS hunters ON participant.ghostHunterID = hunters.id 
                WHERE participant.huntID=?
            """
            params = [id]
            participant = db.execute(sql, params).fetchall()

            sql = """
                SELECT  * FROM message
                JOIN user AS hunters ON message.sender = hunters.id 
                WHERE message.hunt=?
            """
            params = [id]
            message = db.execute(sql, params).fetchall()



        return render_template("pages/huntinginhunt.jinja", message=message, participant=participant)






# SEnd report
# If the user is not logged in, set name as null
# If the user is logged in, set the person who reported it's hunt to their ID

# not cry  I know exactly what i'm doing look at me go. 

@app.post("/sendReport")
def add_hunt():
    location  = request.form.get('location',  '').strip()
    description = request.form.get('description', '').strip()
    if 'id' in session:
        
        with connect_db() as db:
            sql = """
            INSERT INTO reportedHunt ()
            VALUES (?,?, ?)
        """
        params = (session["id"], location, description)
        db.execute(sql, params)
    
    else:
        with connect_db() as db:
            
            sql = """
            INSERT INTO reportedHunt (location, details)
            VALUES (?,?)
            """
            params = (location, description)
            db.execute(sql, params)


    flash("report sent!", "success")
    return redirect("/")








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

