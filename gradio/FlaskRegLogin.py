from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename

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
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Utility function for logging
def log_action(user, action):
    logs_collection.insert_one({
        "user": user,
        "action": action,
        "timestamp": datetime.datetime.now()
    })

# Function to save uploaded photos
def save_photos(user_id, finger_type, photos):
    photo_urls = []
    for i, photo in enumerate(photos):
        if len(photo_urls) < 5:
            # Create a unique filename
            filename = secure_filename(f"{user_id}_{finger_type}_{i+1}.jpg")
            # Ensure the directory exists
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            os.makedirs(os.path.dirname(photo_path), exist_ok=True)
            # Save the photo to the 'static/uploads' directory
            photo.save(photo_path)
            photo_urls.append(url_for('uploaded_file', filename=filename))
    return photo_urls

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
        user_id = session["user_id"] if session["role"] == "Citizen" else data.get("user_id")
        fingerprints = []

        for i, finger_name in enumerate(finger_names):
            finger_type = finger_name.replace(" ", "_")
            photos = request.files.getlist(f"fingerprint_photos_{i}")
            photo_urls = save_photos(user_id, finger_type, photos)
            fingerprints.append({
                "finger_type": finger_type,
                "photos": photo_urls
            })

        # Check if the user already has enrollment data
        if enrollments_collection.find_one({"user_id": user_id}):
            return render_template("error.html", message="User already enrolled.", back_url=url_for("enrollment"))

        enrollment_data = {
            "user_id": user_id,
            "firstname": firstname,
            "lastname": lastname,
            "dob": dob,
            "age": age,
            "gender": gender,
            "contact_info": contact_info,
            "blood_type": blood_type,
            "fingerprints": fingerprints,
            "approved": False if session["role"] == "Citizen" else True
        }

        enrollments_collection.insert_one(enrollment_data)
        log_action(session["username"], "Completed enrollment")
        return render_template("success.html", message="Enrollment successful! Awaiting approval." if session["role"] == "Citizen" else "Enrollment successful!", back_url=url_for("main_page"))

    return render_template("enrollment.html", finger_names=finger_names, role=session["role"])  # A form for enrollment.

# Route: Check and Update Enrollment
@app.route("/check_enrollment", methods=["GET", "POST"])
def check_enrollment():
    if "username" not in session or session["role"] not in ["Police and Investigator"]:
        return redirect(url_for("login"))

    enrollments = enrollments_collection.find({"approved": False})
    return render_template("check_enrollment.html", enrollments=enrollments)

# Route: View Enrollment Details
@app.route("/view_enrollment/<user_id>", methods=["GET", "POST"])
def view_enrollment(user_id):
    if "username" not in session or session["role"] not in ["Police and Investigator"]:
        return redirect(url_for("login"))

    enrollment = enrollments_collection.find_one({"user_id": user_id})
    if not enrollment:
        return render_template("error.html", message="Enrollment data not found.", back_url=url_for("check_enrollment"))

    if request.method == "POST":
        if "approve" in request.form:
            enrollments_collection.update_one({"user_id": user_id}, {"$set": {"approved": True}})
            log_action(session["username"], f"Approved enrollment for user {user_id}")
            return render_template("success.html", message="Enrollment approved.", back_url=url_for("check_enrollment"))
        elif "disapprove" in request.form:
            enrollments_collection.update_one({"user_id": user_id}, {"$set": {"approved": False}})
            log_action(session["username"], f"Disapproved enrollment for user {user_id}")
            return render_template("success.html", message="Enrollment disapproved.", back_url=url_for("check_enrollment"))

    return render_template("view_enrollment.html", enrollment=enrollment)

# Route: Forensic Expertise Page
@app.route("/forensic", methods=["GET"])
def forensic():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    enrollments = enrollments_collection.find()
    return render_template("forensic.html", enrollments=enrollments)

# Route: Upload Image
@app.route("/upload_image", methods=["POST"])
def upload_image():
    if "file" not in request.files:
        return "No file part"
    file = request.files["file"]
    if file.filename == "":
        return "No selected file"
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        return redirect(url_for('uploaded_file', filename=filename))

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Route: Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")