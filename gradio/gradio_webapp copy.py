import gradio as gr
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

# Database Connection
MONGO_URI = "mongodb+srv://host:go2bc2CrPmnTpSh8@cluster0.65enq.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client.latent_fingerprint
users_collection = db.users
logs_collection = db.logs
requests_collection = db.requests

# Globals
roles = ["Police and Investigator", "Forensic Expertise", "Citizen", "Government Official"]

# Utility Functions
def log_action(user, action):
    logs_collection.insert_one({
        "user": user,
        "action": action,
        "timestamp": datetime.datetime.now()
    })

def register_user(username, password, role, additional_info=None):
    if users_collection.find_one({"username": username}):
        return "Username already exists."
    users_collection.insert_one({
        "username": username,
        "password": password,
        "role": role,
        "additional_info": additional_info,
        "approved": False if role != "Citizen" else True
    })
    log_action(username, "Registered as {}".format(role))
    return "Registration successful. Awaiting admin approval." if role != "Citizen" else "Registration successful."

def login_user(username, password):
    user = users_collection.find_one({"username": username, "password": password})
    if user:
        return {"status": "success", "role": user['role'], "approved": user['approved'], "username": username}
    return {"status": "error", "message": "Invalid credentials."}

def get_logs():
    logs = list(logs_collection.find())
    processed_logs = []
    for log in logs:
        processed_logs.append([
            str(log.get("_id", "")),  # Convert ObjectId to string
            log.get("user", ""),
            log.get("action", ""),
            log.get("timestamp", "").strftime("%Y-%m-%d %H:%M:%S") if log.get("timestamp") else "",
        ])
    return processed_logs


def get_users():
    users = list(users_collection.find())
    for user in users:
        user["_id"] = str(user["_id"])
    return users

def update_user_role(user_id, new_role):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return "User not found."
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role}})
    log_action(user["username"], f"Role updated to {new_role}")
    return "Role updated successfully."

# Gradio UI Components
def render_ui(role, username):
    if role == "Police and Investigator":
        return police_ui(username)
    elif role == "Forensic Expertise":
        return forensic_ui(username)
    elif role == "Citizen":
        return citizen_ui(username)
    elif role == "Government Official":
        return admin_ui(username)

def police_ui(username):
    with gr.Blocks() as ui:
        gr.Markdown(f"Welcome, **{username}** (Police and Investigator)")
        with gr.Row():
            enroll_button = gr.Button("Enroll Fingerprints")
            verify_button = gr.Button("Verify Fingerprints")
            identify_button = gr.Button("Identify Fingerprints")
        log_out_button = gr.Button("Logout")
    return ui

def forensic_ui(username):
    with gr.Blocks() as ui:
        gr.Markdown(f"Welcome, **{username}** (Forensic Expertise)")
        with gr.Row():
            review_verification_button = gr.Button("Review Verification Requests")
            review_identification_button = gr.Button("Review Identification Requests")
        log_out_button = gr.Button("Logout")
    return ui

def citizen_ui(username):
    with gr.Blocks() as ui:
        gr.Markdown(f"Welcome, **{username}** (Citizen)")
        enroll_button = gr.Button("Enroll Fingerprints")
        log_out_button = gr.Button("Logout")
    return ui

def admin_ui(username):
    with gr.Blocks() as ui:
        gr.Markdown(f"Welcome, **{username}** (Government Official)")
        with gr.Row():
            manage_users_button = gr.Button("Manage Users")
            view_logs_button = gr.Button("View Logs")
        log_out_button = gr.Button("Logout")
    return ui

def enrollment_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Enrollment Page")
        name = gr.Textbox(label="Name")
        dob = gr.Textbox(label="Date of Birth")
        age = gr.Number(label="Age")
        gender = gr.Dropdown(["Male", "Female", "Other"], label="Gender")
        contact_info = gr.Textbox(label="Contact Info")
        blood_type = gr.Dropdown(["A", "B", "AB", "O"], label="Blood Type")
        fingerprint_photos = gr.File(label="Upload Fingerprint Photos", file_types=[".jpg", ".png"], file_count="multiple")
        submit_button = gr.Button("Submit Enrollment")
    return ui

def verification_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Verification Page")
        database_fingerprint = gr.File(label="Select Fingerprint from Database")
        forensic_expert = gr.Dropdown(["Assign to Forensic Expert"], label="Assign To")
        submit_button = gr.Button("Submit for Verification")
    return ui

def identification_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Identification Page")
        latent_fingerprint = gr.File(label="Upload Latent Fingerprint")
        forensic_expert = gr.Dropdown(["Assign to Forensic Expert"], label="Assign To")
        submit_button = gr.Button("Submit for Identification")
    return ui

def log_management_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Log Management Page")
        logs = gr.Dataframe(
            get_logs(), 
            headers=["ID", "User", "Action", "Timestamp"],  # Define appropriate headers
            label="Activity Logs"
        )
        refresh_button = gr.Button("Refresh Logs")
        refresh_button.click(lambda: get_logs(), None, logs)
    return ui


def manage_users_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Manage Users Page")
        users_list = gr.Dataframe(get_users(), label="Users List")
        role_dropdown = gr.Dropdown(roles, label="Change Role")
        user_id = gr.Textbox(label="User ID")
        update_role_button = gr.Button("Update Role")
        update_status = gr.Textbox(label="Status")
        update_role_button.click(update_user_role, [user_id, role_dropdown], update_status)
    return ui

# Main App
def main():
    user_session = {"username": None, "role": None, "logged_in": False}

    def check_access(page):
        if not user_session["logged_in"]:
            return "Access Denied. Please login first."
        if page == "Enrollment" and user_session["role"] not in ["Police and Investigator", "Citizen"]:
            return "Access Denied. Insufficient permissions."
        if page == "Verification" and user_session["role"] != "Police and Investigator":
            return "Access Denied. Insufficient permissions."
        if page == "Identification" and user_session["role"] != "Police and Investigator":
            return "Access Denied. Insufficient permissions."
        if page == "Logs" and user_session["role"] != "Government Official":
            return "Access Denied. Insufficient permissions."
        if page == "Manage Users" and user_session["role"] != "Government Official":
            return "Access Denied. Insufficient permissions."
        return "Access Granted"

    with gr.Blocks() as app:
        with gr.Tabs():
            with gr.TabItem("Register"):
                username = gr.Textbox(label="Username")
                password = gr.Textbox(label="Password", type="password")
                role = gr.Dropdown(roles, label="Role")
                additional_info = gr.Textbox(label="Additional Info (Optional)")
                register_button = gr.Button("Register")
                output = gr.Textbox(label="Status")
                register_button.click(register_user, [username, password, role, additional_info], output)

            with gr.TabItem("Login"):
                username = gr.Textbox(label="Username")
                password = gr.Textbox(label="Password", type="password")
                login_button = gr.Button("Login")
                output = gr.Textbox(label="Status")

                def login_handler(username, password):
                    result = login_user(username, password)
                    if result["status"] == "success":
                        user_session["username"] = username
                        user_session["role"] = result["role"]
                        user_session["logged_in"] = True
                        return "Login successful!", "success"
                    return result["message"], "error"

                login_button.click(login_handler, [username, password], [output])

            with gr.TabItem("Enrollment"):
                output = gr.Textbox(label="Access Check")
                enrollment_ui()
                gr.Button("Check Access").click(lambda: check_access("Enrollment"), None, output)

            with gr.TabItem("Verification"):
                output = gr.Textbox(label="Access Check")
                verification_ui()
                gr.Button("Check Access").click(lambda: check_access("Verification"), None, output)

            with gr.TabItem("Identification"):
                output = gr.Textbox(label="Access Check")
                identification_ui()
                gr.Button("Check Access").click(lambda: check_access("Identification"), None, output)

            with gr.TabItem("Logs"):
                output = gr.Textbox(label="Access Check")
                log_management_ui()
                gr.Button("Check Access").click(lambda: check_access("Logs"), None, output)

            with gr.TabItem("Manage Users"):
                output = gr.Textbox(label="Access Check")
                manage_users_ui()
                gr.Button("Check Access").click(lambda: check_access("Manage Users"), None, output)

    app.launch()

if __name__ == "__main__":
    main()
