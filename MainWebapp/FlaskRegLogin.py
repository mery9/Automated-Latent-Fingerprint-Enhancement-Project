from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv
import os
from werkzeug.utils import secure_filename
from io import BytesIO
from PIL import Image
import base64

# Load environment variables
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")

# Database connection
client = MongoClient(MONGO_URI)
db = client.latent_fingerprint
users_collection = db.users
enrollments_collection = db.enrollments
logs_collection = db.logs
images_collection = db.images

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

# Function to save uploaded photo
def save_photo(user_id, finger_type, photo):
    # Create a unique filename
    filename = secure_filename(f"{user_id}_{finger_type}.jpg")
    # Ensure the directory exists
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    os.makedirs(os.path.dirname(photo_path), exist_ok=True)
    # Save the photo to the 'static/uploads' directory
    photo.save(photo_path)
    
    # Convert image to base64
    with open(photo_path, 'rb') as f:
        img_data = f.read()
        img_base64 = base64.b64encode(img_data).decode('utf-8')
    
    return img_base64

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
        
        # Check if the user already has enrollment data
        if session["role"] == "Citizen" and enrollments_collection.find_one({"user_id": user_id}):
            return render_template("error.html", message="You have already enrolled.", back_url=url_for("main_page"))

        fingerprints = {}
        if "fingerprints_right_thumb" in request.files:
            fingerprints["fingerprints_right_thumb"] = save_photo(user_id, "Right_Thumb", request.files["fingerprints_right_thumb"])
        if "fingerprints_right_index" in request.files:
            fingerprints["fingerprints_right_index"] = save_photo(user_id, "Right_Index", request.files["fingerprints_right_index"])
        if "fingerprints_right_middle" in request.files:
            fingerprints["fingerprints_right_middle"] = save_photo(user_id, "Right_Middle", request.files["fingerprints_right_middle"])
        if "fingerprints_right_ring" in request.files:
            fingerprints["fingerprints_right_ring"] = save_photo(user_id, "Right_Ring", request.files["fingerprints_right_ring"])
        if "fingerprints_right_little" in request.files:
            fingerprints["fingerprints_right_little"] = save_photo(user_id, "Right_Little", request.files["fingerprints_right_little"])
        if "fingerprints_left_thumb" in request.files:
            fingerprints["fingerprints_left_thumb"] = save_photo(user_id, "Left_Thumb", request.files["fingerprints_left_thumb"])
        if "fingerprints_left_index" in request.files:
            fingerprints["fingerprints_left_index"] = save_photo(user_id, "Left_Index", request.files["fingerprints_left_index"])
        if "fingerprints_left_middle" in request.files:
            fingerprints["fingerprints_left_middle"] = save_photo(user_id, "Left_Middle", request.files["fingerprints_left_middle"])
        if "fingerprints_left_ring" in request.files:
            fingerprints["fingerprints_left_ring"] = save_photo(user_id, "Left_Ring", request.files["fingerprints_left_ring"])
        if "fingerprints_left_little" in request.files:
            fingerprints["fingerprints_left_little"] = save_photo(user_id, "Left_Little", request.files["fingerprints_left_little"])

        enrollment_data = {
            "user_id": user_id,
            "firstname": firstname,
            "lastname": lastname,
            "dob": dob,
            "age": age,
            "gender": gender,
            "contact_info": contact_info,
            "blood_type": blood_type,
            **fingerprints,
            "approved": False if session["role"] == "Citizen" else True
        }

        enrollments_collection.insert_one(enrollment_data)
        log_action(session["username"], "Completed enrollment")
        return render_template("success.html", message="Enrollment successful! Awaiting approval." if session["role"] == "Citizen" else "Enrollment successful!", back_url=url_for("main_page"))

    return render_template("enrollment.html", role=session["role"])  # A form for enrollment.

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

# Route: View Logs
@app.route("/view_logs")
def view_logs():
    if "username" not in session or session["role"] != "Government Official":
        return redirect(url_for("login"))

    logs = logs_collection.find()
    return render_template("view_logs.html", logs=logs)

# Route: Manage Users
@app.route("/manage_users", methods=["GET", "POST"])
def manage_users():
    if "username" not in session or session["role"] != "Government Official":
        return redirect(url_for("login"))

    if request.method == "POST":
        user_id = request.form.get("user_id")
        new_role = request.form.get("new_role")
        new_approval_status = request.form.get("new_approval_status") == "true"

        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role, "approved": new_approval_status}})
        log_action(session["username"], f"Updated user {user_id} role to {new_role} and approval status to {new_approval_status}")

    users = users_collection.find()
    return render_template("manage_users.html", users=users)

# Route: Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")