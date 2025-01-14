import gradio as gr
from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime
from dotenv import load_dotenv
import os

# Database Connection
load_dotenv()
MONGO_URI = os.getenv("MONGO_URI")
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
            str(log.get("_id", "")),
            log.get("user", ""),
            log.get("action", ""),
            log.get("timestamp", datetime.datetime.now()).strftime("%Y-%m-%d %H:%M:%S")
        ])
    return processed_logs

def get_users():
    users = list(users_collection.find())
    processed_users = []
    for user in users:
        processed_users.append([
            str(user.get("_id", "")),
            user.get("username", ""),
            user.get("role", ""),
            user.get("approved", False)
        ])
    return processed_users

def update_user_role(user_id, new_role):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return "User not found."
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role}})
    log_action(user["username"], f"Role updated to {new_role}")
    return "Role updated successfully."

# Function to toggle user approval status
def toggle_user_approval(user_id):
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        return "User not found."
    new_status = not user.get("approved", False)
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"approved": new_status}})
    return f"User approval status changed to {'True' if new_status else 'False'}."

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
            gr.Button("Enroll Fingerprints")
            gr.Button("Verify Fingerprints")
            gr.Button("Identify Fingerprints")
        gr.Button("Logout")
    return ui

def forensic_ui(username):
    with gr.Blocks() as ui:
        gr.Markdown(f"Welcome, **{username}** (Forensic Expertise)")
        with gr.Row():
            gr.Button("Review Verification Requests")
            gr.Button("Review Identification Requests")
        gr.Button("Logout")
    return ui

def citizen_ui(username):
    with gr.Blocks() as ui:
        gr.Markdown(f"Welcome, **{username}** (Citizen)")
        gr.Button("Enroll Fingerprints")
        gr.Button("Logout")
    return ui

def admin_ui(username):
    with gr.Blocks() as ui:
        gr.Markdown(f"Welcome, **{username}** (Government Official)")
        with gr.Row():
            gr.Button("Manage Users")
            gr.Button("View Logs")
        gr.Button("Logout")
    return ui

def enrollment_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Enrollment Page")
        gr.Textbox(label="Name")
        gr.Textbox(label="Date of Birth")
        gr.Number(label="Age")
        gr.Dropdown(["Male", "Female", "Other"], label="Gender")
        gr.Textbox(label="Contact Info")
        gr.Dropdown(["A", "B", "AB", "O"], label="Blood Type")
        gr.File(label="Upload Fingerprint Photos", file_types=[".jpg", ".png"], file_count="multiple")
        gr.Button("Submit Enrollment")
    return ui

def verification_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Verification Page")
        gr.File(label="Select Fingerprint from Database")
        gr.Dropdown(["Assign to Forensic Expert"], label="Assign To")
        gr.Button("Submit for Verification")
    return ui

def identification_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Identification Page")
        gr.File(label="Upload Latent Fingerprint")
        gr.Dropdown(["Assign to Forensic Expert"], label="Assign To")
        gr.Button("Submit for Identification")
    return ui

def log_management_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### Log Management Page")
        headers = ["ID", "User", "Action", "Timestamp"]
        logs = gr.Dataframe(get_logs(), headers=headers, label="Activity Logs")
        refresh_button = gr.Button("Refresh Logs")
        refresh_button.click(lambda: get_logs(), None, logs)
    return ui


def manage_users_ui():
    with gr.Blocks() as ui:
        gr.Markdown("### User Management")
        headers = ["ID", "Username", "Role", "Approved"]
        users = gr.Dataframe(get_users(), headers=headers, label="User Management")
        
        refresh_button = gr.Button("Refresh Users")
        refresh_button.click(lambda: get_users(), None, users)

        role_dropdown = gr.Dropdown(roles, label="Change Role")
        user_id_input = gr.Textbox(label="User ID")
        update_role_button = gr.Button("Update Role")
        update_status = gr.Textbox(label="Status")
        update_role_button.click(update_user_role, [user_id_input, role_dropdown], update_status)

        toggle_approval_button = gr.Button("Toggle Approval Status")
        toggle_status_output = gr.Textbox(label="Status")
        toggle_approval_button.click(toggle_user_approval, [user_id_input], toggle_status_output)
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

        with gr.TabItem("Verification"):
            verification_ui()

        with gr.TabItem("Identification"):
            identification_ui()

        with gr.TabItem("Log Management"):
            log_management_ui()

        with gr.TabItem("User Management"):
            manage_users_ui()


    app.launch()

if __name__ == "__main__":
    main()
