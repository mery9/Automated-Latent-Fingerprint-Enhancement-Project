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
import subprocess

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
latent_fingerprints_collection = db.latent_fingerprints_images

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

@app.route("/test")
def test():
    return render_template("test.html")

@app.route("/")
def home():
    return redirect(url_for("login"))

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
        return render_template("error.html", message="Enrollment data not found.", back_url=url_for("view_approved_enrollments"))

    if request.method == "POST" and not enrollment["approved"]:
        if "approve" in request.form:
            enrollments_collection.update_one({"user_id": user_id}, {"$set": {"approved": True}})
            log_action(session["username"], f"Approved enrollment for user {user_id}")
            return render_template("success.html", message="Enrollment approved.", back_url=url_for("view_approved_enrollments"))
        elif "disapprove" in request.form:
            enrollments_collection.update_one({"user_id": user_id}, {"$set": {"approved": False}})
            log_action(session["username"], f"Disapproved enrollment for user {user_id}")
            return render_template("success.html", message="Enrollment disapproved.", back_url=url_for("view_approved_enrollments"))

    return render_template("view_enrollment.html", enrollment=enrollment)

# Route: View Approved Enrollments
@app.route("/view_approved_enrollments")
def view_approved_enrollments():
    if "username" not in session or session["role"] != "Police and Investigator":
        return redirect(url_for("login"))

    enrollments = enrollments_collection.find({"approved": True})
    return render_template("view_approved_enrollments.html", enrollments=enrollments)

# Route: Upload Latent Fingerprint
@app.route("/upload_latent_fingerprint", methods=["GET", "POST"])
def upload_latent_fingerprint():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    if request.method == "POST":
        if "fingerprint_photo" in request.files:
            photo = request.files["fingerprint_photo"]
            filename = secure_filename(photo.filename)
            photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(photo_path)
            
            # Convert image to base64
            with open(photo_path, 'rb') as f:
                img_data = f.read()
                img_base64 = base64.b64encode(img_data).decode('utf-8')
            
            # Insert into database
            latent_fingerprints_collection.insert_one({
                "filename": filename,
                "image_data": img_base64,
                "uploaded_by": session["username"],
                "timestamp": datetime.datetime.now()
            })
            log_action(session["username"], "Uploaded latent fingerprint")

            return render_template("success.html", message="Latent fingerprint uploaded successfully.", back_url=url_for("main_page"))

    return render_template("upload_latent_fingerprint.html")

# Route: View Latent Fingerprints
@app.route("/view_latent_fingerprints")
def view_latent_fingerprints():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    fingerprints = latent_fingerprints_collection.find()
    return render_template("view_latent_fingerprints.html", fingerprints=fingerprints)

# Route: Enhance Latent Fingerprint
@app.route("/enhance_latent_fingerprint/<fingerprint_id>", methods=["GET", "POST"])
def enhance_latent_fingerprint(fingerprint_id):
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    fingerprint = latent_fingerprints_collection.find_one({"_id": ObjectId(fingerprint_id)})
    if not fingerprint:
        return render_template("error.html", message="Fingerprint not found.", back_url=url_for("view_latent_fingerprints"))

    if request.method == "POST":
        enhanced_image_data = request.form.get("enhanced_image_data")
        if enhanced_image_data:
            latent_fingerprints_collection.update_one(
                {"_id": ObjectId(fingerprint_id)},
                {"$set": {"enhanced_image_data": enhanced_image_data}}
            )
            log_action(session["username"], f"Enhanced latent fingerprint {fingerprint_id}")
            return render_template("success.html", message="Enhanced fingerprint saved successfully.", back_url=url_for("view_latent_fingerprints"))

    return render_template("enhance_latent_fingerprint.html", fingerprint=fingerprint)

# Route: Match Fingerprints
@app.route("/match_fingerprints", methods=["GET", "POST"])
def match_fingerprints():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    similarity_score = None

    if request.method == "POST":
        if "fingerprint1" in request.files and "fingerprint2" in request.files:
            fingerprint1 = request.files["fingerprint1"]
            fingerprint2 = request.files["fingerprint2"]

            # Save the uploaded files temporarily
            fingerprint1_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fingerprint1.filename))
            fingerprint2_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(fingerprint2.filename))
            fingerprint1.save(fingerprint1_path)
            fingerprint2.save(fingerprint2_path)

            print(f"Saved fingerprint1 to {fingerprint1_path}")
            print(f"Saved fingerprint2 to {fingerprint2_path}")

            try:
                # Call the Java program to match fingerprints
                result = subprocess.run(
                    ["java", "-cp", "D:/Work/Project/WebApp/sourceafis-project/target/sourceafis-project-1.0-SNAPSHOT-jar-with-dependencies.jar", "com.example.FingerprintMatching", fingerprint1_path, fingerprint2_path],
                    capture_output=True,
                    text=True,
                    shell=True  # Add shell=True to ensure the command is executed in the shell
                )

                print("Java program output:")
                print(result.stdout)
                print(result.stderr)

                # Extract the similarity score from the Java program output
                for line in result.stdout.splitlines():
                    if "Similarity score:" in line:
                        similarity_score = line.split(":")[1].strip()
                        print(f"Extracted similarity score: {similarity_score}")
                        break

            finally:
                # Clean up the temporary files
                if os.path.exists(fingerprint1_path):
                    os.remove(fingerprint1_path)
                if os.path.exists(fingerprint2_path):
                    os.remove(fingerprint2_path)

    return render_template("match_fingerprints.html", similarity_score=similarity_score, role=session["role"])

# Route: Manage Users
@app.route("/manage_users", methods=["GET", "POST"])
def manage_users():
    if "username" not in session or session["role"] != "Government Official":
        return redirect(url_for("login"))

    search_query = request.form.get("search", "").strip()

    query = {}
    if search_query:
        query["$or"] = [
            {"_id": {"$regex": search_query, "$options": "i"}},
            {"username": {"$regex": search_query, "$options": "i"}},
            {"role": {"$regex": search_query, "$options": "i"}},
            {"approved": {"$regex": search_query, "$options": "i"}}
        ]

    if request.method == "POST" and "user_id" in request.form:
        user_id = request.form.get("user_id")
        new_role = request.form.get("new_role")
        new_approval_status = request.form.get("new_approval_status") == "true"

        users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role, "approved": new_approval_status}})
        log_action(session["username"], f"Updated user {user_id} role to {new_role} and approval status to {new_approval_status}")

    users = list(users_collection.find(query))
    return render_template("manage_users.html", users=users, search_query=search_query)

# Route: View Logs
@app.route("/view_logs", methods=["GET", "POST"])
def view_logs():
    if "username" not in session or session["role"] != "Government Official":
        return redirect(url_for("login"))

    page = int(request.args.get("page", 1))
    per_page = 25
    search_query = request.form.get("search", "")
    
    query = {}
    if search_query:
        try:
            object_id = ObjectId(search_query)
            query["_id"] = object_id
        except:
            query = {
                "$or": [
                    {"user": {"$regex": search_query, "$options": "i"}},
                    {"action": {"$regex": search_query, "$options": "i"}},
                    {"timestamp": {"$regex": search_query, "$options": "i"}}
                ]
            }
    
    total_logs = logs_collection.count_documents(query)
    total_pages = (total_logs + per_page - 1) // per_page
    logs = list(logs_collection.find(query).skip((page - 1) * per_page).limit(per_page))
    
    # Format the timestamp correctly
    for log in logs:
        log["timestamp"] = log["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")
    
    return render_template("view_logs.html", logs=logs, page=page, total_pages=total_pages, search_query=search_query)

# Route: Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")