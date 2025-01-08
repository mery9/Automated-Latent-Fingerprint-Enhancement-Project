from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv
import os
import gradio as gr
import threading

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Database connection
client = MongoClient(MONGO_URI)
db = client.latent_fingerprint
users_collection = db.users
enrollments_collection = db.enrollments
logs_collection = db.logs

# Flask app setup
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"

# Utility function for logging
def log_action(user, action):
    logs_collection.insert_one({
        "user": user,
        "action": action,
        "timestamp": datetime.datetime.now()
    })

# Route: Home
@app.route("/")
def home():
    return render_template("home.html")  # A simple HTML page with "Register" and "Login" links.
    
# Route: Register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        data = request.form
        username = data.get("username").lower()
        password = data.get("password")
        role = data.get("role")
        additional_info = data.get("additional_info")

        # Check if the username already exists
        if users_collection.find_one({"username": username}):
            return render_template("error.html", message="Username already exists.", back_url=url_for("register"))
        
        # Insert user into the database
        users_collection.insert_one({
            "username": username,
            "password": password,
            "role": role,
            "additional_info": additional_info,
            "approved": False if role != "Citizen" else True
        })
        log_action(username, f"Registered as {role}")
        return render_template("success.html", message="Registration successful! Awaiting approval." if role != "Citizen" else "Registration successful!", back_url=url_for("home"))
    
    return render_template("register.html")  # A simple form for registration.

# Route: Login
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.form
        username = data.get("username").lower()
        password = data.get("password")

        # Authenticate user
        user = users_collection.find_one({"username": username, "password": password})
        if user:
            if not user["approved"]:
                return render_template("error.html", message="Account not approved yet.", back_url=url_for("login"))
            session["user_id"] = str(user["_id"])
            session["username"] = username
            session["role"] = user["role"]
            return redirect(url_for("main_page"))  # Redirect to the main page
        return render_template("error.html", message="Invalid credentials.", back_url=url_for("login"))

    return render_template("login.html")  # A simple form for login.

# Route: Main Page
@app.route("/main")
def main_page():
    if "username" not in session:
        return redirect(url_for("login"))

    user_id = session["user_id"]
    username = session["username"]
    role = session["role"]

    return render_template("main.html", user_id=user_id, username=username, role=role)

# Route: Enrollment
@app.route("/enrollment", methods=["GET", "POST"])
def enrollment():
    if "username" not in session or session["role"] not in ["Citizen", "Police and Investigator"]:
        return redirect(url_for("login"))

    finger_names = [
        "Right Thumb", "Right Index", "Right Middle", "Right Ring", "Right Little",
        "Left Thumb", "Left Index", "Left Middle", "Left Ring", "Left Little"
    ]

    if request.method == "POST":
        data = request.form
        firstname = data.get("firstname")
        lastname = data.get("lastname")
        dob = data.get("dob")
        age = data.get("age")
        gender = data.get("gender")
        contact_info = data.get("contact_info")
        blood_type = data.get("blood_type")
        fingerprints = []

        for i, finger_name in enumerate(finger_names):
            finger_type = finger_name
            photos = request.files.getlist(f"fingerprint_photos_{i}")
            photo_urls = []
            for photo in photos:
                if len(photo_urls) < 5:
                    # Save photo and get URL (this is a placeholder, implement actual saving logic)
                    photo_url = f"/path/to/photo/{photo.filename}"
                    photo_urls.append(photo_url)
            fingerprints.append({
                "finger_type": finger_type,
                "photos": photo_urls
            })

        enrollment_data = {
            "user_id": session["user_id"],
            "firstname": firstname,
            "lastname": lastname,
            "dob": dob,
            "age": age,
            "gender": gender,
            "contact_info": contact_info,
            "blood_type": blood_type,
            "fingerprints": fingerprints
        }

        enrollments_collection.insert_one(enrollment_data)
        log_action(session["username"], "Completed enrollment")
        return render_template("success.html", message="Enrollment successful!", back_url=url_for("main_page"))

    return render_template("enrollment.html", finger_names=finger_names)  # A form for enrollment.

# Route: Forensic Expertise Page
@app.route("/forensic", methods=["GET"])
def forensic():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    enrollments = enrollments_collection.find()
    return render_template("forensic.html", enrollments=enrollments)

# Route: Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

# Route: Gradio App
@app.route("/gradio")
def gradio_app():
    if "username" not in session:
        return redirect(url_for("login"))

    username = session["username"]
    role = session["role"]

    # Redirect to the Gradio app running on a different port with username and role as query parameters
    return redirect(f"http://127.0.0.1:7860?username={username}&role={role}")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")