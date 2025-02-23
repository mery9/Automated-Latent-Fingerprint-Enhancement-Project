from flask import Flask, render_template, request, redirect, url_for, session, send_file
from pymongo import MongoClient
from bson.objectid import ObjectId
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import gridfs
import os
import datetime
import subprocess
import threading
import shutil
from LatentsEnhancement.experiment.latent_fingerprint_enhancement import TestNetwork
from PIL import Image

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
identification_results_collection = db.identification_results
enhanced_images_collection = db.enhanced_images
fs = gridfs.GridFS(db)

# Flask app setup
app = Flask(__name__)
app.secret_key = "your_secret_key"
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Ensure the upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Utility function for logging
def log_action(user, action):
    ip_address = request.remote_addr
    logs_collection.insert_one({
        "user": user,
        "action": action,
        "ip_address": ip_address,
        "timestamp": datetime.datetime.now()
    })

# Function to save uploaded photo to GridFS
def save_photo(user_id, finger_type, photo):
    filename = f"{user_id}_{finger_type}.jpg"
    file_id = fs.put(photo, filename=filename)
    return file_id

# Function to calculate shard number
def calculate_shard_number(user_id, num_shards=4):
    return int(user_id, 16) % num_shards

# Function to get the next sequence number
def get_next_sequence_number():
    last_enrollment = enrollments_collection.find_one(sort=[("sequence_number", -1)])
    if last_enrollment and "sequence_number" in last_enrollment:
        return last_enrollment["sequence_number"] + 1
    return 1

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
            log_action(username, "Logged in")
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
        firstname = data.get("firstname").strip()
        lastname = data.get("lastname").strip()
        gender = data.get("gender").strip()
        contact_info = data.get("contact_info").strip()
        blood_type = data.get("blood_type").strip()
        fingerprint_capture_date = data.get("fingerprint_capture_date").strip()
        user_id = session["user_id"] if session["role"] == "Citizen" else data.get("user_id").strip()
        username = session["username"]
        
        # Check if the user already has enrollment data
        if session["role"] == "Citizen" and enrollments_collection.find_one({"user_id": user_id}):
            return render_template("error.html", message="You have already enrolled.", back_url=url_for("main_page"))

        # Calculate shard number
        shard_number = calculate_shard_number(user_id)

        # Get the next sequence number
        sequence_number = get_next_sequence_number()

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
            "username": username,
            "firstname": firstname,
            "lastname": lastname,
            "gender": gender,
            "contact_info": contact_info,
            "blood_type": blood_type,
            "fingerprint_capture_date": fingerprint_capture_date,
            "shard_number": shard_number,
            "sequence_number": sequence_number,
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

# Route: Serve Image from GridFS
@app.route("/image/<file_id>")
def serve_image(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        return send_file(file, mimetype='image/jpeg')
    except Exception as e:
        return str(e)

# Route: View Enrollment Details
@app.route("/view_enrollment/<user_id>", methods=["GET", "POST"])
def view_enrollment(user_id):
    if "username" not in session or session["role"] not in ["Police and Investigator"]:
        return redirect(url_for("login"))

    enrollment = enrollments_collection.find_one({"user_id": user_id})
    if not enrollment:
        return render_template("error.html", message="Enrollment data not found.", back_url=url_for("view_approved_enrollments"))

    fingerprint_image_urls = {}
    for key in enrollment.keys():
        if key.startswith("fingerprints_"):
            fingerprint_type = key.replace("fingerprints_", "")
            fingerprint_image_urls[fingerprint_type] = url_for('serve_image', file_id=enrollment[key])

    if request.method == "POST":
        if "approve" in request.form:
            enrollments_collection.update_one({"user_id": user_id}, {"$set": {"approved": True}})
            log_action(session["username"], f"Approved enrollment for user {user_id}")
            return render_template("success.html", message="Enrollment approved.", back_url=url_for("check_enrollment"))
        elif "disapprove" in request.form:
            enrollments_collection.delete_one({"user_id": user_id})
            log_action(session["username"], f"Disapproved and deleted enrollment for user {user_id}")
            return render_template("success.html", message="Enrollment disapproved and deleted.", back_url=url_for("check_enrollment"))

    log_action(session["username"], f"Viewed enrollment details for user {user_id}")
    return render_template("view_enrollment.html", enrollment=enrollment, fingerprint_image_urls=fingerprint_image_urls)

# Route: View Approved Enrollments
@app.route("/view_approved_enrollments")
def view_approved_enrollments():
    if "username" not in session or session["role"] != "Police and Investigator":
        return redirect(url_for("login"))

    sort_by = request.args.get("sort_by", "sequence_number")
    filter_gender = request.args.get("filter_gender", "")
    filter_blood_type = request.args.get("filter_blood_type", "")
    search_shard = request.args.get("search_shard", "")
    search_firstname = request.args.get("search_firstname", "")
    search_lastname = request.args.get("search_lastname", "")
    search_sequence_number = request.args.get("search_sequence_number", "")
    error_message = None

    query = {"approved": True}
    if filter_gender:
        query["gender"] = filter_gender
    if filter_blood_type:
        query["blood_type"] = filter_blood_type
    if search_shard:
        try:
            query["shard_number"] = int(search_shard)
        except ValueError:
            error_message = "Shard number must be an integer."
    if search_firstname:
        if not search_firstname.isalpha():
            error_message = "Firstname must contain only letters."
        else:
            query["firstname"] = {"$regex": search_firstname, "$options": "i"}
    if search_lastname:
        if not search_lastname.isalpha():
            error_message = "Lastname must contain only letters."
        else:
            query["lastname"] = {"$regex": search_lastname, "$options": "i"}
    if search_sequence_number:
        try:
            query["sequence_number"] = int(search_sequence_number)
        except ValueError:
            error_message = "Sequence number must be an integer."

    enrollments = enrollments_collection.find(query)
    
    if sort_by == "blood_type":
        blood_type_order = {"A": 1, "B": 2, "O": 3, "AB": 4}
        enrollments = sorted(enrollments, key=lambda x: blood_type_order.get(x["blood_type"], 5))
    elif sort_by == "gender":
        gender_order = {"Male": 1, "Female": 2}
        enrollments = sorted(enrollments, key=lambda x: gender_order.get(x["gender"], 3))
    elif sort_by == "sequence_number":
        enrollments = enrollments.sort("sequence_number")
    else:
        enrollments = enrollments.sort(sort_by)

    log_action(session["username"], "Viewed approved enrollments with sorting and filtering")
    return render_template("view_approved_enrollments.html", enrollments=enrollments, error_message=error_message)

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

    user_data = None
    similarity_score = None
    fingerprint_image_urls = {}
    available_fingerprint_types = []

    if request.method == "POST":
        if "search_user" in request.form:
            user_id = request.form.get("user_id")
            user_data = enrollments_collection.find_one({"user_id": user_id})
            if not user_data:
                log_action(session["username"], f"User not found for matching fingerprints: {user_id}")
                return render_template("error.html", message="User not found.", back_url=url_for("match_fingerprints"))

            # Get available fingerprint types and their image URLs for the user
            available_fingerprint_types = [key.replace("fingerprints_", "") for key in user_data.keys() if key.startswith("fingerprints_")]
            for fingerprint_type in available_fingerprint_types:
                fingerprint_image_urls[fingerprint_type] = url_for('serve_image', file_id=user_data[f"fingerprints_{fingerprint_type}"])

        elif "match_fingerprints" in request.form:
            fingerprint1_id = request.form.get("fingerprint1_id")
            fingerprint1_type = request.form.get("fingerprint1_type")
            latent_fingerprint = request.files.get("latent_fingerprint")

            if fingerprint1_id and fingerprint1_type and latent_fingerprint:
                fingerprint1 = enrollments_collection.find_one({"_id": ObjectId(fingerprint1_id)})

                if fingerprint1:
                    fingerprint1_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{fingerprint1_id}_{fingerprint1_type}.jpg")
                    latent_fingerprint_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(latent_fingerprint.filename))
                    latent_fingerprint.save(latent_fingerprint_path)

                    with open(fingerprint1_path, "wb") as f1:
                        f1.write(fs.get(fingerprint1[f"fingerprints_{fingerprint1_type}"]).read())

                    fingerprint_image_urls[fingerprint1_type] = url_for('serve_image', file_id=fingerprint1[f"fingerprints_{fingerprint1_type}"])

                    try:
                        # Call the Java program to match fingerprints
                        result = subprocess.run(
                            ["java", "-cp", "D:/Work/Project/WebApp/sourceafis-project/target/sourceafis-project-1.0-SNAPSHOT-jar-with-dependencies.jar", "com.example.FingerprintMatching", fingerprint1_path, latent_fingerprint_path],
                            capture_output=True,
                            text=True,
                            shell=True
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

                        # Log the action
                        log_action(session["username"], f"Matched fingerprints: {fingerprint1_id} ({fingerprint1_type}) with latent fingerprint. Similarity score: {similarity_score}")

                    finally:
                        # Clean up the temporary files
                        if os.path.exists(fingerprint1_path):
                            os.remove(fingerprint1_path)
                        if os.path.exists(latent_fingerprint_path):
                            os.remove(latent_fingerprint_path)

    log_action(session["username"], "Accessed match fingerprints page")
    return render_template("match_fingerprints.html", user_data=user_data, similarity_score=similarity_score, fingerprint_image_urls=fingerprint_image_urls, available_fingerprint_types=available_fingerprint_types, role=session["role"])

# Route: Enhance Fingerprint
@app.route("/enhance_fingerprint", methods=["GET", "POST"])
def enhance_fingerprint():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    if request.method == "POST":
        if "fingerprint_photos" in request.files:
            files = request.files.getlist("fingerprint_photos")
            unique_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
            upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'enhance_input_{unique_id}')
            os.makedirs(upload_folder, exist_ok=True)

            for file in files:
                filename = secure_filename(file.filename)
                file_path = os.path.join(upload_folder, filename)
                file.save(file_path)

            # Create a log entry with "processing" status
            log_id = enhanced_images_collection.insert_one({
                "user": session["username"],
                "files": [file.filename for file in files],
                "results": [],
                "status": "processing",
                "timestamp": datetime.datetime.now()
            }).inserted_id

            # Start the background process
            threading.Thread(target=process_enhancement, args=(log_id, upload_folder, session["username"], unique_id)).start()
            return render_template("success.html", message="Enhancement process started. You can check the results in the enhancement logs.", back_url=url_for("view_enhancement_logs"))

    return render_template("enhance_fingerprint.html", role=session["role"])

# Function to process enhancement in the background
def process_enhancement(log_id, upload_folder, username, unique_id):
    output_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'enhance_output_{unique_id}')
    os.makedirs(output_folder, exist_ok=True)
    results = []

    try:
        # Resize and convert images to grayscale
        for filename in os.listdir(upload_folder):
            file_path = os.path.join(upload_folder, filename)
            with Image.open(file_path) as img:
                # Resize image dynamically
                max_size = (1500, 1500)
                img.thumbnail(max_size, Image.ANTIALIAS)
                
                # Convert to grayscale
                grayscale_img = img.convert("L")
                grayscale_img.save(file_path)

        # Run the enhancement tool
        test_network = TestNetwork()
        test_network.args.latent_fingerprint_dir = upload_folder
        test_network.args.out_dir = output_folder
        test_network.run_test()

        # Collect enhanced images and save to database
        for filename in os.listdir(upload_folder):
            enhanced_file_path = os.path.join(output_folder, filename)
            if os.path.exists(enhanced_file_path):
                with open(enhanced_file_path, "rb") as f:
                    file_id = fs.put(f, filename=filename)
                    results.append(file_id)

        # Update the log entry with the results
        enhanced_images_collection.update_one(
            {"_id": ObjectId(log_id)},
            {"$set": {"results": results, "status": "completed"}}
        )

    finally:
        # Clean up input and output folders
        if os.path.exists(upload_folder):
            shutil.rmtree(upload_folder)
        if os.path.exists(output_folder):
            shutil.rmtree(output_folder)

# Route: View Enhancement Logs
@app.route("/view_enhancement_logs", methods=["GET", "POST"])
def view_enhancement_logs():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    if request.method == "POST":
        log_id = request.form.get("log_id")
        if log_id:
            enhanced_images_collection.delete_one({"_id": ObjectId(log_id)})
            log_action(session["username"], f"Deleted enhancement log {log_id}")
            return redirect(url_for("view_enhancement_logs"))

    logs = list(enhanced_images_collection.find({"user": session["username"]}).sort("timestamp", -1))
    log_action(session["username"], "Viewed enhancement logs")
    return render_template("view_enhancement_logs.html", logs=logs, role=session["role"])

# Route: Download Enhanced Image
@app.route("/download_enhanced_image/<file_id>")
def download_enhanced_image(file_id):
    try:
        file = fs.get(ObjectId(file_id))
        log_action(session["username"], f"Downloaded enhanced image {file_id}")
        return send_file(file, mimetype='image/jpeg', as_attachment=True, download_name=file.filename)
    except Exception as e:
        log_action(session["username"], f"Failed to download enhanced image {file_id}: {str(e)}")
        return str(e)

# Function to process identification in the background
def process_identification(log_id, uploaded_fingerprint_id, username, upload_folder):
    enrollments = list(enrollments_collection.find({"approved": True}))
    results = []

    try:
        uploaded_fingerprint_path = os.path.join(upload_folder, f"{uploaded_fingerprint_id}.jpg")
        with open(uploaded_fingerprint_path, "wb") as f:
            f.write(fs.get(uploaded_fingerprint_id).read())

        # Match against all enrollment fingerprints
        for enrollment in enrollments:
            for fingerprint_type in ["right_thumb", "right_index", "right_middle", "right_ring", "right_little",
                                     "left_thumb", "left_index", "left_middle", "left_ring", "left_little"]:
                if f"fingerprints_{fingerprint_type}" in enrollment:
                    fingerprint2_path = os.path.join(upload_folder, f"{enrollment['_id']}_{fingerprint_type}.jpg")

                    with open(fingerprint2_path, "wb") as f2:
                        f2.write(fs.get(enrollment[f"fingerprints_{fingerprint_type}"]).read())

                    result = subprocess.run(
                        ["java", "-cp", "D:/Work/Project/WebApp/sourceafis-project/target/sourceafis-project-1.0-SNAPSHOT-jar-with-dependencies.jar", "com.example.FingerprintMatching", uploaded_fingerprint_path, fingerprint2_path],
                        capture_output=True,
                        text=True,
                        shell=True
                    )

                    print("Java program output:")
                    print(result.stdout)
                    print(result.stderr)

                    for line in result.stdout.splitlines():
                        if "Similarity score:" in line:
                            similarity_score = float(line.split(":")[1].strip())
                            results.append({
                                "user_id": enrollment["user_id"],
                                "fingerprint_type": fingerprint_type,
                                "similarity_score": similarity_score,
                                f"fingerprints_{fingerprint_type}": enrollment[f"fingerprints_{fingerprint_type}"]
                            })
                            break

                    if os.path.exists(fingerprint2_path):
                        os.remove(fingerprint2_path)

        # Sort results by similarity score in descending order and take top 10
        results.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = results[:10]

        # Update the log entry with the results
        identification_results_collection.update_one(
            {"_id": ObjectId(log_id)},
            {"$set": {"results": results, "status": "completed"}}
        )

        log_action(username, f"Processed identification for log {log_id}")

    finally:
        if os.path.exists(uploaded_fingerprint_path):
            os.remove(uploaded_fingerprint_path)
        if os.path.exists(upload_folder):
            shutil.rmtree(upload_folder)

# Route: Identify Fingerprints
@app.route("/identify_fingerprints", methods=["GET", "POST"])
def identify_fingerprints():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    if request.method == "POST":
        if "fingerprint_photos" in request.files:
            files = request.files.getlist("fingerprint_photos")
            for file in files:
                filename = secure_filename(file.filename)
                file_id = fs.put(file, filename=filename)

                # Create a unique folder for each file
                unique_id = datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")
                upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], f'identify_input_{unique_id}')
                os.makedirs(upload_folder, exist_ok=True)

                file_path = os.path.join(upload_folder, filename)
                with open(file_path, "wb") as f:
                    f.write(fs.get(file_id).read())

                # Create a log entry with "processing" status
                log_id = identification_results_collection.insert_one({
                    "user": session["username"],
                    "uploaded_fingerprint": file_id,
                    "uploaded_fingerprint_filename": filename,
                    "results": [],
                    "status": "processing",
                    "timestamp": datetime.datetime.now()
                }).inserted_id

                # Start the background process for each file
                threading.Thread(target=process_identification, args=(log_id, file_id, session["username"], upload_folder)).start()
                log_action(session["username"], f"Started identification process for log {log_id}")

            return render_template("success.html", message="Identification processes started. You can check the results in the logs.", back_url=url_for("identify_fingerprints"))

    log_action(session["username"], "Accessed identify fingerprints page")
    return render_template("identify_fingerprints.html", role=session["role"])

# Route: View Identification Logs
@app.route("/view_identification_logs", methods=["GET", "POST"])
def view_identification_logs():
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    if request.method == "POST":
        log_id = request.form.get("log_id")
        if log_id:
            identification_results_collection.delete_one({"_id": ObjectId(log_id)})
            log_action(session["username"], f"Deleted identification log {log_id}")
            return redirect(url_for("view_identification_logs"))

    logs = list(identification_results_collection.find({"user": session["username"]}).sort("timestamp", -1))
    log_action(session["username"], "Viewed identification logs")
    return render_template("view_identification_logs.html", logs=logs, role=session["role"])

# Route: View Identification Result
@app.route("/view_identification_result/<log_id>")
def view_identification_result(log_id):
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    log = identification_results_collection.find_one({"_id": ObjectId(log_id)})
    if not log:
        return render_template("error.html", message="Log not found.", back_url=url_for("view_identification_logs"))

    results = log.get("results", [])
    enrollments = []

    for result in results:
        enrollment = enrollments_collection.find_one({"user_id": result["user_id"]})
        if enrollment:
            fingerprint_key = f"fingerprints_{result['fingerprint_type']}"
            if fingerprint_key in enrollment:
                fingerprint_image_url = url_for('serve_image', file_id=enrollment[fingerprint_key])
                enrollments.append({
                    "user_id": result["user_id"],
                    "fingerprint_type": result["fingerprint_type"],
                    "similarity_score": result["similarity_score"],
                    "enrollment": enrollment,
                    "fingerprint_image_url": fingerprint_image_url
                })
                print(f"Added fingerprint image URL: {fingerprint_image_url}")

    uploaded_fingerprint_id = log.get("uploaded_fingerprint")
    uploaded_fingerprint_url = url_for('serve_image', file_id=uploaded_fingerprint_id)
    print(f"Uploaded fingerprint URL: {uploaded_fingerprint_url}")
    print(f"Enrollments: {enrollments}")
    log_action(session["username"], f"Viewed identification result for log {log_id}")
    return render_template("view_identification_result.html", log=log, enrollments=enrollments, role=session["role"], uploaded_fingerprint_url=uploaded_fingerprint_url)

# Route: Get Latent Fingerprint Image
@app.route("/get_latent_fingerprint_image/<fingerprint_id>")
def get_latent_fingerprint_image(fingerprint_id):
    fingerprint = latent_fingerprints_collection.find_one({"_id": ObjectId(fingerprint_id)})
    if fingerprint:
        image_data = fingerprint.get("image_data", "")
        return {"image": image_data}
    return {"image": None}

# Route: Get Fingerprint Image
@app.route("/get_fingerprint_image/<fingerprint_id>/<fingerprint_type>")
def get_fingerprint_image(fingerprint_id, fingerprint_type):
    fingerprint = enrollments_collection.find_one({"_id": ObjectId(fingerprint_id)})
    if fingerprint:
        image_data = fingerprint.get(f"fingerprints_{fingerprint_type}", "")
        return {"image": image_data}
    return {"image": None}

# Route: Get Available Fingerprints
@app.route("/get_available_fingerprints/<fingerprint_id>")
def get_available_fingerprints(fingerprint_id):
    fingerprint = enrollments_collection.find_one({"_id": ObjectId(fingerprint_id)})
    if fingerprint:
        available_fingerprints = [key.replace("fingerprints_", "") for key in fingerprint.keys() if key.startswith("fingerprints_") and fingerprint[key]]
        return {"available_fingerprints": available_fingerprints}
    return {"available_fingerprints": []}

# Route: Manage Users
@app.route("/manage_users", methods=["GET", "POST"])
def manage_users():
    if "username" not in session or session["role"] != "Government Official":
        return redirect(url_for("login"))

    sort_by = request.args.get("sort_by", "username")
    filter_role = request.args.get("filter_role", "")
    filter_approved = request.args.get("filter_approved", "")
    search_username = request.args.get("search_username", "")
    
    query = {}
    if filter_role:
        query["role"] = filter_role
    if filter_approved:
        query["approved"] = filter_approved == "true"
    if search_username:
        query["username"] = {"$regex": search_username, "$options": "i"}

    users = users_collection.find(query)
    
    if sort_by == "role":
        role_order = {"Government Official": 1, "Forensic Expertise": 2, "Police and Investigator": 3, "Citizen": 4}
        users = sorted(users, key=lambda x: role_order.get(x["role"], 5))
    else:
        users = users.sort(sort_by)

    log_action(session["username"], "Viewed and managed users with sorting and filtering")
    return render_template("manage_users.html", users=users, sort_by=sort_by, filter_role=filter_role, filter_approved=filter_approved, search_username=search_username)

def delete_user_data(user_id):
    # Delete user from users collection
    users_collection.delete_one({"_id": ObjectId(user_id)})
    
    # Delete user's enrollments
    enrollments_collection.delete_many({"user_id": user_id})
    
    # Delete user's logs
    logs_collection.delete_many({"user": user_id})
    
    # Delete user's identification results
    identification_results_collection.delete_many({"user": user_id})
    
    # Delete user's enhanced images
    enhanced_images_collection.delete_many({"user": user_id})

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
                    {"timestamp": {"$regex": search_query, "$options": "i"}},
                    {"ip_address": {"$regex": search_query, "$options": "i"}}
                ]
            }
    
    total_logs = logs_collection.count_documents(query)
    total_pages = (total_logs + per_page - 1) // per_page
    logs = list(logs_collection.find(query).skip((page - 1) * per_page).limit(per_page))
    
    # Format the timestamp correctly
    for log in logs:
        log["timestamp"] = log["timestamp"].strftime("%Y-%m-%dT%H:%M:%S")
    
    log_action(session["username"], "Viewed logs")
    return render_template("view_logs.html", logs=logs, page=page, total_pages=total_pages, search_query=search_query)

# Route: View Enhancement Result
@app.route("/view_enhancement_result/<log_id>")
def view_enhancement_result(log_id):
    if "username" not in session or session["role"] != "Forensic Expertise":
        return redirect(url_for("login"))

    log = enhanced_images_collection.find_one({"_id": ObjectId(log_id)})
    if not log:
        return render_template("error.html", message="Log not found.", back_url=url_for("view_enhancement_logs"))

    results = log.get("results", [])
    enhanced_images = []

    for result in results:
        file_id = result
        file = fs.get(file_id)
        file_url = url_for('serve_image', file_id=file_id)
        enhanced_images.append((file_url, file.filename))

    log_action(session["username"], f"Viewed enhancement result for log {log_id}")
    return render_template("view_enhancement_result.html", log=log, enhanced_images=enhanced_images, role=session["role"])

# Custom 404 Error Handler
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Route: Logout
@app.route("/logout")
def logout():
    username = session.get("username")
    session.clear()
    if username:
        log_action(username, "Logged out")
    return redirect(url_for("home"))

if __name__== "__main__":
    app.run(debug=True, host="0.0.0.0")
