#================================================👻===========
# PARATRA
# By YOUR NAME HERE 👻
#========👻===================================================

from flask import Flask, request, session, render_template, flash, redirect, send_file, make_response, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
from urllib.parse import urlencode, quote
from os import getenv
from io import BytesIO
import html
import requests
import os
from app.helpers import *
import uuid
from datetime import *



# Create the app
app = Flask(__name__)



# TODO 
# Cannot set a date in the past
# Delete my account




# - see hunt ui
# - send hunt feedback 
# - fuck thats a databsase thing isn't it
#  - fit database
#  - stop at nice park benches to delay arrival at bridges to cross



# Images code

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')
   
   



#===========================================================
# App Routes Handlers
#===========================================================

#-----------------------------------------------------------
# Welcome page
#-----------------------------------------------------------


#-----------------------------------------------------------
# Creature list page - Show all the creatures
#-----------------------------------------------------------


#-----------------------------------------------------------
# Help page - Show some help
#-----------------------------------------------------------






 












# Get all the dates from the reported hunt table. 
# for each hunt in hunt
# if the reported hunt date is today slash whenever
# change the status. 

# 

@app.get("/")
def show_home():

    with connect_db() as db:
            sql = """
            SELECT * FROM reportedHunt
            ORDER BY reportedHunt.dateReported DESC 

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


    with connect_db() as db:
        sql = "SELECT id FROM user WHERE username=?"
        params = (username,)
        not_user = db.execute(sql, params).fetchone()

        if  not_user:
            flash(f"Username '{username}' already exists", "error")
            return redirect("/signup_page")

        pass_hash = generate_password_hash(password)

        sql = """
            INSERT INTO user (forename, surname, username, passwordHash)
            VALUES (?, ?, ?, ?)
        """
        params = (forename, surname, username, pass_hash)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("/login_page")

# rendering 
@app.get("/report_ghost")
def report_ghost():
    return render_template("pages/reportForm.jinja")

# joining hunt - id given being the hunt id
@app.post("/join_hunt/<int:id>")
@login_required
def join_hunt(id):

# rip out the check if user exists from the signup table and put it here. 
    with connect_db() as db:
        # Show if there's a row where the hunt id = the id given AND ghost hunter id = the id
        sql = "SELECT * FROM participant WHERE ghostHunterID=? AND huntID=?"
        params = [session["user"]["id"],id]
        signedUp = db.execute(sql, params).fetchone()

        if  signedUp:
            flash("You have already signed up for this hunt!", "error")
            return redirect("/")
        
        sql = "SELECT ghostHunterID  FROM participant WHERE huntID=?"
        params = [id]
        leader = db.execute(sql, params).fetchall()
        
        if not leader:
            sql = """
            UPDATE reportedHunt 
            SET (huntLeader)=?
            WHERE id=?
            """
            params = (session["user"]["id"], id)
            db.execute(sql, params)

        
        sql = """
            INSERT INTO participant (huntID, ghostHunterID )
            VALUES (?, ?)
        """
        params = (id, session["user"]["id"])
        db.execute(sql, params)

        flash("You have signed up for this hunt.")
        return redirect("/")

#update the date of hunt in the database.
@app.post("/set_date/<int:id>")
@login_required
def set_date(id):
    raw = request.form.get("date_of_hunt", "").strip()
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        flash("Invalid date.", "error")
        return redirect("/")

    with connect_db() as db:
        db.execute(
            "UPDATE reportedHunt SET date_of_hunt = ? WHERE id = ?",
            (dt.isoformat(), id),
        )
    flash("Date set!", "success")
    return redirect("/")



# Send the hunt report
@app.post("/send_report/<int:id>")
@login_required
def send_report(id):
    description = request.form.get("description", "").strip()
    next_action = request.form.get("next_action", "").strip()
    images = request.files.getlist("images")

    with connect_db() as db:
        db.execute(
            """
            UPDATE reportedHunt
            SET description = ?, recommended_next_action = ?, status = 'Report Submitted'
            WHERE id = ?
            """,
            (description, next_action, id),
        )

        for img in images:
            # An empty file input submits one blank part; skip it
            if not img or img.filename == "":
                continue

            filename = secure_filename(img.filename)
            unique_filename = f"{uuid.uuid4().hex[:12]}_{filename}"
            img.save(os.path.join(UPLOAD_FOLDER, unique_filename))

            db.execute(
                "INSERT INTO image (hunt, image, before_hunt) VALUES (?, ?, ?)",
                (id, unique_filename, 0),
            )

    flash("Report Sent!", "success")
    return redirect("/")

@app.post("/hunt/<int:id>/end")
@login_required
def end_hunt(id):
    with connect_db() as db:
        sql = """
        UPDATE reportedHunt 
        SET status = "Hunt Ended"
        WHERE id =?
        """
        params = (id,)
        db.execute(sql, params)

        flash("Hunt ended", "success")
    return redirect(f"/view_hunt/{id}")

#view specific hunt
@app.get("/view_hunt/<int:id>")
@login_required
def view_hunt(id):
    with connect_db() as db:
        sql = """
            SELECT  
            reportedHunt.id  AS hunt_id,
            reportedHunt.huntLeader    ,
            reportedHunt.reportedBy ,
            reportedHunt.details   , 
            reportedHunt.description,
            reportedHunt.recommended_next_action,
            reportedHunt.dateReported,
            reportedHunt.date_of_hunt,
            reportedHunt.status,
            reportedHunt.location,
            leader.username AS leader_username,
            reporter.username AS reporter_username
            FROM reportedHunt
            LEFT JOIN user AS reporter ON reportedHunt.reportedBy = reporter.id
            LEFT JOIN user AS leader ON reportedHunt.huntLeader = leader.id
            WHERE reportedHunt.id=?
          
        """
        params = (id,)
        hunt = db.execute(sql, params).fetchone()

        sql = """
            SELECT  * FROM image
            WHERE hunt=?
        """
        params = (id,)
        photos = db.execute(sql, params).fetchall()


        user_id = session["user"]["id"]
        sql = "SELECT DATE(date_of_hunt) AS date_of_hunt FROM reportedHunt WHERE id=?"
        params = (id,)
        row = db.execute(sql, params).fetchone()
        hunt_date = row['date_of_hunt']
        todays_date = date.today()

        row = db.execute("SELECT date_of_hunt, status FROM reportedHunt WHERE id = ?", (id,)).fetchone()

        if row["date_of_hunt"] and row["status"] == "open":
            hunt_dt = datetime.fromisoformat(row["date_of_hunt"])
            if datetime.now(timezone.utc) >= hunt_dt:
                print("THIS IS TRUE")     
                sql = """
            UPDATE reportedHunt 
            SET status= "hunting" 
            WHERE id = ?;
                    """
                params = (id,)
                db.execute(sql, params)

        # Hunting
        sql = """
            SELECT  * FROM participant
            JOIN user AS hunters ON participant.ghostHunterID = hunters.id 
            WHERE participant.huntID=?
        """
        params = [id]
        participants = db.execute(sql, params).fetchall()


        sql = """
            SELECT  * FROM participant WHERE participant.ghostHunterID=?
        """
        params = (session["user"]["id"],)
        signed_up = db.execute(sql, params).fetchall()


        # Selecting the whole time, not formatting it to put in the javascript countdown. 
        sql = "SELECT date_of_hunt AS time_of_hunt FROM reportedHunt WHERE id=?"
        params = [id,]
        row = db.execute(sql, params).fetchone()
        hunt_time = row['time_of_hunt']

        print("----------------------------------------------")
        address = hunt['location']
        print(address)
        address = quote(address)
        print(address)
        osm_api_url = f"https://nominatim.openstreetmap.org/search?q=${address}&format=json"
        print(osm_api_url)
        headers = { 'User-Agent': 'GhostHunters/1.0 (polly@ghosts.boo)'}
        response = requests.get(osm_api_url, headers=headers)
        print(response)
        data = response.json()
        print(data)
        print(len(data))
        
        try:
            place = data[0]
            lat = place["lat"]
            lon = place["lon"]
        except: 
            flash("No location found for this address! If this is your hunt, try a different address!", "error")
            return redirect("/")


        # Hunting in hunt: 
        #  if their username is in the list of participating users then set it to true. else set it to false

        sql = """
                SELECT  * FROM message
                JOIN user AS hunters ON message.sender = hunters.id 
                WHERE message.hunt=?
            """
        params = [id]
        message = db.execute(sql, params).fetchall()
        

        

        return render_template("pages/hunt.jinja", 
                            hunt=hunt, 
                            user_id=user_id, 
                            hunt_date=hunt_date, 
                            todays_date=todays_date, 
                            participants=participants, 
                            hunt_time=hunt_time,
                            lat=lat,
                            lon=lon,
                            messages=message,
                            signed_up=signed_up,
                            photos=photos)
    
@app.get("/messages/<int:hunt_id>/")
@login_required
def get_messages(hunt_id):
    after = request.args.get("after", 0, type=int)
    with connect_db() as db:
        rows = db.execute("""
            SELECT message.id, message.body, user.forename, user.surname
            FROM message
            JOIN user ON user.id = message.sender
            WHERE message.hunt = ? AND message.id > ?
            ORDER BY message.id
        """, (hunt_id, after)).fetchall()
    return jsonify([dict(r) for r in rows])

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




# Leader system. 
# Each hunt has a 'leader'
# If 'people in hunt' = 0 then you're the leader
# yay

# SEnd report
# If the user is not logged in, set name as null
# If the user is logged in, set the person who reported it's hunt to their ID

# not cry  I know exactly what i'm doing look at me go. 

@app.get("/logout")
@login_required
def logout_admin():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")    

@app.post("/sendReport")

def add_hunt():
    description = request.form.get("description", "").strip()
    images = request.files.getlist("images")
    street = request.form.get("street address-search address-search", "").strip()
    town = request.form.get("town", "").strip()
    country = request.form.get("country", "").strip()

    
    location = " ".join(part for part in (street, town, country) if part)
    for i in range (50):
        print(street)
    
    user_id = None
    if session.get("user") and session.get("logged_in"):
        user_id = session["user"]["id"]

    with connect_db() as db:
        cursor = db.execute(
            "INSERT INTO reportedHunt (reportedBy, location, details) VALUES (?, ?, ?)",
            (user_id, location, description),
        )
        hunt_id = cursor.lastrowid

        for img in images:

            if not img or img.filename == "":
                continue

            filename = secure_filename(img.filename)
            unique_filename = f"{uuid.uuid4().hex[:12]}_{filename}"
            img.save(os.path.join(UPLOAD_FOLDER, unique_filename))

            db.execute(
                "INSERT INTO image (hunt, image, before_hunt) VALUES (?, ?, ?)",
                (hunt_id, unique_filename, 1),
            )

    flash("report sent!", "success")
    return redirect("/")


@app.post("/message/<int:id>/")
@login_required
def add_message(id):
    user_id = session["user"]["id"]
    body = request.form.get("body", "").strip()
    if not body:
        return jsonify(error="Empty message"), 400

    with connect_db() as db:
        db.execute(
            "INSERT INTO message (sender, hunt, body) VALUES (?, ?, ?)",
            (user_id, id, body),
        )
    return jsonify(ok=True)

@app.get("/profile/<int:id>")
@login_required
def see_profile(id):
     
     with connect_db() as db:
            sql = """
                SELECT  * FROM user
                WHERE id=?
            """

            params = (id,)
            user = db.execute(sql, params).fetchone()


            sql = """
                SELECT  * FROM participant AS hunts
                LEFT JOIN reportedHunt ON hunts.huntID == reportedHunt.id
                WHERE ghostHunterID=?
            """
            params = (id,)
            previous_hunts = db.execute(sql, params).fetchall()

            sql = """
                SELECT  * FROM reportedHunt 
                WHERE reportedBy=?
            """
            params = (id,)
            reported_hunts = db.execute(sql, params).fetchall()


            return render_template("pages/profile.jinja", user=user, previous_hunts=previous_hunts, reported_hunts=reported_hunts)
     

@app.get("/profile/<int:id>/edit")
@login_required
def edit_profile(id):
    return render_template("pages/profile_edit.jinja")

@app.post("/edit_profile")
@login_required
def submit_profile_edit():
     id = session["user"]["id"]
     bio  = request.form.get('bio',  '').strip()
     profile_image = request.files.get('image_file', None)
     
     if not profile_image or profile_image.filename == '':
        flash("There was a problem uploading the image", "error")
        return redirect("/")
    
    # Sanitise filename and make it unique
     filename = secure_filename(profile_image.filename)
     random_prefix = uuid.uuid4().hex[:12]
     unique_filename = f"{random_prefix}_{filename}"

    # Get the path of the upload folder
     filepath = os.path.join(UPLOAD_FOLDER, unique_filename)

    # Save file to disk
     profile_image.save(filepath)

    # Add the form data and the upload filename to the DB
     with connect_db() as db:
           sql = """
            UPDATE user 
            SET bio=?, profile_picture=?
            WHERE id=?
            """
           params = (bio, unique_filename, id)
           db.execute(sql, params)
           flash("Profile updated", "success")
           return redirect(f"/profile/{id}")
     

@app.get("/delete_profile")
@login_required
def delete_profile():
     with connect_db() as db:
           sql = """
            DELETE FROM user
            WHERE id=?
            """
           params = (session["user"]["id"],)
           db.execute(sql, params)
           
           session.clear()
     flash("Account deleted", "success")
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

