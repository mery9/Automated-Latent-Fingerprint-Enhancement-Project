import gradio as gr
from pymongo import MongoClient
from bson.objectid import ObjectId
from datetime import datetime
import hashlib
import os

# MongoDB setup
MONGO_URI = "mongodb+srv://host:go2bc2CrPmnTpSh8@cluster0.65enq.mongodb.net/"
client = MongoClient(MONGO_URI)
db = client.latent_fingerprint_app
users_collection = db.users
logs_collection = db.logs
fingerprints_collection = db.fingerprints

# Helper functions
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def add_log(username, action):
    logs_collection.insert_one({
        "username": username,
        "action": action,
        "timestamp": datetime.now()
    })

def authenticate_user(username, password):
    user = users_collection.find_one({"username": username, "password": hash_password(password)})
    if user:
        return user
    return None

def get_role_based_ui(role):
    if role == "police_and_investigator":
        return police_ui
    elif role == "forensic_expertise":
        return forensic_ui
    elif role == "citizen":
        return citizen_ui
    elif role == "government_official":
        return admin_ui
    else:
        return None

# Pages for roles
def register_page(username, password, role):
    if users_collection.find_one({"username": username}):
        return "Username already exists."
    users_collection.insert_one({"username": username, "password": hash_password(password), "role": role, "status": "pending"})
    add_log(username, "Registered as " + role)
    return "Registration successful. Waiting for admin approval."

def login_page(username, password):
    user = authenticate_user(username, password)
    if not user:
        return "Invalid credentials."
    if user['status'] != "approved":
        return "Your account is not yet approved."
    add_log(username, "Logged in")
    return f"Welcome, {username}. Your role: {user['role']}", user

def enrollment_page(username, name, dob, age, gender, contact, blood_type, fingerprints):
    fingerprints_collection.insert_one({
        "username": username,
        "name": name,
        "dob": dob,
        "age": age,
        "gender": gender,
        "contact": contact,
        "blood_type": blood_type,
        "fingerprints": fingerprints,
        "status": "pending"
    })
    add_log(username, "Enrolled fingerprints")
    return "Enrollment data submitted. Waiting for police review."

def verification_page(username, fingerprint_id):
    fingerprint = fingerprints_collection.find_one({"_id": ObjectId(fingerprint_id)})
    if not fingerprint:
        return "Fingerprint not found."
    add_log(username, "Requested verification for fingerprint " + fingerprint_id)
    # Notify forensic expertise (could be implemented via messaging system)
    return "Verification request sent to forensic expertise."

def identification_page(username, fingerprint_id):
    fingerprint = fingerprints_collection.find_one({"_id": ObjectId(fingerprint_id)})
    if not fingerprint:
        return "Fingerprint not found."
    add_log(username, "Requested identification for fingerprint " + fingerprint_id)
    # Notify forensic expertise (could be implemented via messaging system)
    return "Identification request sent to forensic expertise."

def admin_page(username):
    logs = list(logs_collection.find())
    users = list(users_collection.find())
    add_log(username, "Viewed logs and user management")
    return logs, users

def update_user_role(admin_username, user_id, new_role):
    users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": {"role": new_role, "status": "approved"}})
    add_log(admin_username, f"Updated role of user {user_id} to {new_role}")
    return "User role updated."

# Define UI for roles
def citizen_ui():
    return gr.Interface(fn=enrollment_page, inputs=["text", "text", "text", "number", "text", "text", "text", "file"], outputs="text")

def police_ui():
    return gr.Interface(fn=verification_page, inputs=["text", "text"], outputs="text")

def forensic_ui():
    return gr.Interface(fn=verification_page, inputs=["text", "text"], outputs="text")

def admin_ui():
    return gr.Interface(fn=admin_page, inputs=["text"], outputs="json")

# Main app
def main():
    try:
        app = gr.Blocks()
        with app:
            gr.Markdown("# Latent Fingerprint Enhancement System")
            with gr.Row():
                with gr.Column():
                    register = gr.Interface(fn=register_page, 
                                            inputs=["text", gr.Textbox(type="password"), "text"], outputs="text")

                    login = gr.Interface(fn=login_page, inputs=[gr.Textbox(label="Username", placeholder="Enter your username"), gr.Textbox(label="Password", placeholder="Enter your password", type="password")], outputs=[gr.Textbox(label="Message"), gr.JSON(label="User Details")]
)

                with gr.Column():
                    logout = gr.Button("Logout")
                    gr.Markdown("Welcome user interface will appear here after login")
        
        app.launch()
    finally:
        client.close()

if __name__ == "__main__":
    main()
