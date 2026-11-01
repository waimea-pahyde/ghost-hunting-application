#================================================👻===========
# PARATRACK 
# By Polly :D 👻
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

UPLOAD_FOLDER = os.path.join('app', 'static', 'uploads')


# Create the app
app = Flask(__name__)

# ----------------------------#
#           Home page            #
# ----------------------------#
@app.get("/")
def show_home():
    with connect_db() as db:
            # -------------------------------------------------------
            # Retrieving all hunts from the database to display
            sql = """
            SELECT * FROM reported_hunt
            ORDER BY reported_hunt.date_reported DESC 

            """
            hunts = db.execute(sql).fetchall()

            
            # -------------------------------------------------------
            # Checking if the user has any hunts, to display 
            # 'my hunts' section on page.
            
            my_hunts = None
            
            if session.get("user") and session.get("logged_in"): #Checking if there is a user and if it's logged in 
                sql = """
                SELECT *
                FROM participant 
                JOIN reported_hunt ON participant.huntID = reported_hunt.id
                WHERE participant.ghost_hunter_ID = ? 
                """
                params = [session["user"]["id"]]
                my_hunts = db.execute(sql, params).fetchall()

            # -------------------------------------------------------
            # Going through all the hunts and setting a lon & a 
            # lat, to display  on the map. 
            
            for hunt in hunts:
                if hunt["lat"] == None:
                    address = hunt['location'] # Get an address, feed it into the openstreetmap API, return a json
                    address = quote(address)
                    osm_api_url = f"https://nominatim.openstreetmap.org/search?q=${address}&format=json"
                    headers = { 'User-Agent': 'GhostHunters/1.0 (polly@ghosts.boo)'}
                    response = requests.get(osm_api_url, headers=headers)
                    data = response.json()
                    try: # Mapbox API can be funny with certain addresses, + currently no prevention for manual address input. 
                            # Check if an address actually returned nicely. 
                            place = data[0]
                            lat = place["lat"]
                            lon = place["lon"]
                            db.execute("""
                        UPDATE reported_hunt
                        SET lat=?, lon=?               
                        WHERE id=?
                    """,
                       (lat, lon, hunt["id"]))
                        
                    except:
                            continue
                    else:
                        continue    
            return render_template("pages/home.jinja", hunts=hunts, my_hunts=my_hunts)


# ----------------------------#
#           Login page             #
# ----------------------------#
@app.get("/login_page")
def show_login():
    return render_template("pages/login.jinja")


# ----------------------------#
#           Login Route           #
# ----------------------------#
@app.post("/login")
def login_user():
    username = request.form.get('username', '').strip().lower()
    password = request.form.get('password', '').strip()

    with connect_db() as db:
        sql = """
            SELECT id, forename, surname, password_hash
            FROM user
            WHERE LOWER(username) = ?
        """
        params = (username,)
        user = db.execute(sql, params).fetchone()

        if not user:
            flash(f"Unknown user", "error")
            return redirect("/login_page")

        if not check_password_hash(user["password_hash"], password):
            flash(f"Incorrect password", "error")
            return redirect("/login_page")

        session["logged_in"] = True
        session["user"] = {
            "id": user["id"],
            "username": username,
            "forename": user["forename"],
            "surname":  user["surname"]
        }

        flash("Login successful", "success")
        return redirect("/")


# ----------------------------#
#           Signup Page           #
# ----------------------------# 
@app.get("/signup_page")
def show_signup():
    return render_template("pages/signup.jinja")


# ----------------------------#
#           Signup Route         #
# ----------------------------# 
@app.post("/signup")
def add_user():
    forename = request.form.get('forename', '').strip()
    surname  = request.form.get('surname',  '').strip()
    username = request.form.get('username', '').strip()
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
            INSERT INTO user (forename, surname, username, password_hash)
            VALUES (?, ?, ?, ?)
        """
        params = (forename, surname, username, pass_hash)
        db.execute(sql, params)

        flash("Account created. Please login", "success")
        return redirect("/login_page")


# ----------------------------#
#   Ghost Reporting Page    #
# ----------------------------# 
@app.get("/hunt/report")
def report_ghost():
    return render_template("pages/report_form.jinja")



# ----------------------------#
#           Joining a hunt       #
# ----------------------------# 
@app.post("/hunt/<int:id>/join")
@login_required
def join_hunt(id):

    # -------------------------------------------------------
    # Checking if the user is already signed up
    with connect_db() as db:
        sql = "SELECT * FROM participant WHERE ghost_hunter_ID=? AND huntID=?"
        params = [session["user"]["id"],id]
        signed_up = db.execute(sql, params).fetchone()

        if  signed_up:
            flash("You have already signed up for this hunt!", "error")
            return redirect("/")
        
        # -------------------------------------------------------
        # Checking if there's any users under this hunt
        sql = "SELECT ghost_hunter_ID  FROM participant WHERE huntID=?"
        params = [id]
        leader = db.execute(sql, params).fetchall()
        
        if not leader: # If none, set the current user to the leader. 
            sql = """
            UPDATE reported_hunt 
            SET (hunt_leader)=?
            WHERE id=?
            """
            params = (session["user"]["id"], id)
            db.execute(sql, params)

        # -------------------------------------------------------
        # Add the user into the hunt
        sql = """
            INSERT INTO participant (huntID, ghost_hunter_ID )
            VALUES (?, ?)
        """
        params = (id, session["user"]["id"])
        db.execute(sql, params)

        flash("You have signed up for this hunt.")
        return redirect("/")


# ----------------------------#
#      Updating hunt date    #
# ----------------------------# 
@app.post("/hunt/<int:id>/set-date")
@login_required
def set_date(id):
    # -------------------------------------------------------
    # Get the raw date from the form on the hunt page
    raw = request.form.get("date_of_hunt", "").strip()
    
    try: #turning it into UTC
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00")).astimezone(timezone.utc)
    except ValueError:
        flash("Invalid date.", "error")
        return redirect("/")

    with connect_db() as db: 
        db.execute(
            "UPDATE reported_hunt SET date_of_hunt = ? WHERE id = ?",
            (dt.isoformat(), id),
        )
    flash("Date set!", "success")
    return redirect("/")



# ---------------------------------------#
# Sending After-Hunt Report Route #
# ---------------------------------------# 
@app.post("/hunt/<int:id>/send-report")
@login_required
def send_report(id):
    description = request.form.get("description", "").strip()
    next_action = request.form.get("next_action", "").strip()
    images = request.files.getlist("images")

    with connect_db() as db:
        # -------------------------------------------------------
        # Get everything from the form on the hunt page,
        # Set status to 'Report Submitted'
        
        db.execute(
            """
            UPDATE reported_hunt
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


# ----------------------------#
#     Ending Hunt Route      #
# ----------------------------# 
@app.post("/hunt/<int:id>/end")
@login_required
def end_hunt(id):
    with connect_db() as db:
        sql = """
        UPDATE reported_hunt 
        SET status = "Hunt Ended"
        WHERE id =?
        """
        params = (id,)
        db.execute(sql, params)

        flash("Hunt ended", "success")
    return redirect(f"/view_hunt/{id}")

# -----------------------------#
#              Hunt Page           #
# ----------------------------# 
@app.get("/hunt/<int:id>")
@login_required
def view_hunt(id):
        # -------------------------------------------------------
        # Get every bit of information about the hunt
    with connect_db() as db:
        sql = """
            SELECT 
            reported_hunt.*, 
            reported_hunt.id  AS hunt_id,
            leader.username AS leader_username,
            reporter.username AS reporter_username,
            leader.id AS leader_id,
            reporter.id AS reporter_id
            FROM reported_hunt
            LEFT JOIN user AS reporter ON reported_hunt.reported_by = reporter.id
            LEFT JOIN user AS leader ON reported_hunt.hunt_leader = leader.id
            WHERE reported_hunt.id=?
          
        """
        params = (id,)
        hunt = db.execute(sql, params).fetchone()

        # -------------------------------------------------------
        # Get all associated images
        sql = """
            SELECT  * FROM image
            WHERE hunt=?
        """
        params = (id,)
        photos = db.execute(sql, params).fetchall()

        
        # -------------------------------------------------------
        # Getting the date of the hunt and changing the status
        
        user_id = session["user"]["id"]
        # *re*get the date, this time feeding it through DATE()
        sql = "SELECT DATE(date_of_hunt) AS date_of_hunt FROM reported_hunt WHERE id=?"
        params = (id,)
        row = db.execute(sql, params).fetchone()
        hunt_date = row['date_of_hunt']
        todays_date = date.today()

        row = db.execute("SELECT date_of_hunt, status FROM reported_hunt WHERE id = ?", (id,)).fetchone()
        
        # If it's been set, and the status hasn't *already* changed, check if the date is todays date. 
        if row["date_of_hunt"] and row["status"] == "open":
            hunt_dt = datetime.fromisoformat(row["date_of_hunt"])
            
            # If it is, set the hunt status to 'hunting'
            if datetime.now(timezone.utc) >= hunt_dt: 
                sql = """
            UPDATE reported_hunt 
            SET status= "hunting" 
            WHERE id = ?;
                    """
                params = (id,)
                db.execute(sql, params)

        # -------------------------------------------------------
        # Getting a list of participants for this hunt
        sql = """
            SELECT  * FROM participant
            JOIN user AS hunters ON participant.ghost_hunter_ID = hunters.id 
            WHERE participant.huntID=?
        """
        params = [id]
        participants = db.execute(sql, params).fetchall()

        # -------------------------------------------------------
        # Checking if the user has already signed up for this hunt
        sql = """
            SELECT  * FROM participant WHERE participant.ghost_hunter_ID=? AND participant.huntID=?
        """
        params = (session["user"]["id"], id)
        signed_up = db.execute(sql, params).fetchone()


        # -------------------------------------------------------
        # Getting the date for the last time now, 
        # this time not formatting it

        sql = "SELECT date_of_hunt AS time_of_hunt FROM reported_hunt WHERE id=?"
        params = [id,]
        row = db.execute(sql, params).fetchone()
        hunt_time = row['time_of_hunt']

        # -------------------------------------------------------
        # Getting all the messages
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
                            messages=message,
                            signed_up=signed_up,
                            photos=photos)
    

# ----------------------------#
#     Getting messages        #
# ----------------------------# 
@app.get("/messages/<int:hunt_id>/")
@login_required
def get_messages(hunt_id):
    
    # Get all the messages and feed them into a json
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

# ----------------------------#
#     Logout User                #
# ----------------------------# 
@app.get("/logout")
@login_required
def logout_admin():
    session.clear()
    flash(f"You have been logged out", "success")
    return redirect("/")    

# -----------------------------#
# Send Ghost Report Route #
# -----------------------------# 
@app.post("/hunt/report/send")
def add_hunt():
    description = request.form.get("description", "").strip()
    images = request.files.getlist("images")
    street = request.form.get("street address-search", "").strip()
    town = request.form.get("town", "").strip()
    country = request.form.get("country", "").strip()

    #-------------------------------------------------------------------
    #Get all the parts, and chuck them together in a big long one
    # That can then be fed into the osm api
    location = " ".join(part for part in (street, town, country) if part)
    

    user_id = None
    if session.get("user") and session.get("logged_in"):
        user_id = session["user"]["id"]

    # Set the cursor to the new hunt id
    with connect_db() as db:
        cursor = db.execute(
            "INSERT INTO reported_hunt (reported_by, location, details) VALUES (?, ?, ?)",
            (user_id, location, description),
        )
        hunt_id = cursor.lastrowid

        # Get all the images sent in
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

# ----------------------------#
#     Send Message Route   #
# ----------------------------# 
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


# ----------------------------#
#           Profile Page           #
# ----------------------------# 
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
                LEFT JOIN reported_hunt ON hunts.huntID == reported_hunt.id
                WHERE ghost_hunter_ID=?
            """
            params = (id,)
            previous_hunts = db.execute(sql, params).fetchall()

            sql = """
                SELECT  * FROM reported_hunt 
                WHERE reported_by=?
            """
            params = (id,)
            reported_hunts = db.execute(sql, params).fetchall()


            return render_template("pages/profile.jinja", user=user, previous_hunts=previous_hunts, reported_hunts=reported_hunts)
     
# ----------------------------#
#     Edit Profile Page         #
# ----------------------------# 
@app.get("/profile/<int:id>/edit")
@login_required
def edit_profile(id):
    return render_template("pages/profile_edit.jinja")

# ----------------------------#
#     Edit profile route        #
# ----------------------------# 
@app.post("/edit_profile")
@login_required
def submit_profile_edit():
     id = session["user"]["id"]
     bio  = request.form.get('bio',  '').strip()
     profile_image = request.files.get('image_file', None)
     
    #  When they edit their bio and don't change the image
     if not profile_image and bio != None:
        with connect_db() as db:
           sql = """
            UPDATE user 
            SET bio=?
            WHERE id=?
            """
           params = (bio, id)
           db.execute(sql, params)
           flash("Profile updated", "success")
           return redirect(f"/profile/{id}")
            


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
     
# ----------------------------#
#     Delete profile route    #
# ----------------------------# 
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

