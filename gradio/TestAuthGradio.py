import gradio as gr
from flask import Flask, request, redirect, url_for

app = Flask(__name__)

# Sample data for users
users = {
    "admin": {"password": "adminpass", "role": "admin"},
    "user": {"password": "userpass", "role": "user"},
    "guest": {"password": "guestpass", "role": "guest"},
    "superadmin": {"password": "superadminpass", "role": "superadmin"}
}

# Define Gradio UIs for each role
def admin_ui():
    return "Admin Interface"

def user_ui():
    return "User Interface"

def guest_ui():
    return "Guest Interface"

def superadmin_ui():
    return "Superadmin Interface"

admin_interface = gr.Interface(fn=admin_ui, inputs=[], outputs="text")
user_interface = gr.Interface(fn=user_ui, inputs=[], outputs="text")
guest_interface = gr.Interface(fn=guest_ui, inputs=[], outputs="text")
superadmin_interface = gr.Interface(fn=superadmin_ui, inputs=[], outputs="text")

@app.route('/')
def home():
    return '''
    <form action="/login" method="POST">
        <input name="username" placeholder="Username">
        <input name="password" type="password" placeholder="Password">
        <button type="submit">Login</button>
    </form>
    '''

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    if username in users and users[username]['password'] == password:
        role = users[username]['role']
        if role == 'admin':
            return redirect(url_for('admin'))
        elif role == 'user':
            return redirect(url_for('user'))
        elif role == 'guest':
            return redirect(url_for('guest'))
        elif role == 'superadmin':
            return redirect(url_for('superadmin'))
    return 'Invalid credentials'

@app.route('/admin')
def admin():
    return admin_interface.launch(share=False)

@app.route('/user')
def user():
    return user_interface.launch(share=False)

@app.route('/guest')
def guest():
    return guest_interface.launch(share=False)

@app.route('/superadmin')
def superadmin():
    return superadmin_interface.launch(share=False)

if __name__ == "__main__":
    app.run(debug=True)
