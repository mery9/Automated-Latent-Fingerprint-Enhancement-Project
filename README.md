# WebApp Project!

## Overview

This project is a web application for managing fingerprint enrollments, matching fingerprints, and enhancing latent fingerprints. It includes features for user registration, login, and role-based access control.

## Features

- User Registration and Login
- Role-based Access Control (Citizen, Police and Investigator, Forensic Expertise, Government Official)
- Fingerprint Enrollment
- Fingerprint Matching
- Latent Fingerprint Enhancement
- System Logs

## Setup

### Prerequisites

- Python 3.x
- MongoDB
- Java 11
- Maven
- Nvidia CUDA 

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/mery9/Automated-Latent-Fingerprint-Enhancement-Project.git
   ```

2. Create a virtual environment and activate it:
   ```bash
   sudo apt install python3.10-venv
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Python dependencies**:
   ```sh
   pip install -r requirements.txt
   pip install torch torchvision torchaudio --extra-index-url https://download.pytorch.org/whl/cu118
   ```

4. **Set up the Java environment**:
   - Ensure that Java is installed and the `JAVA_HOME` environment variable is set.

5. **Build the Maven project**:
   ```sh
   cd sourceafis-project
   mvn clean install
   cd ..
   ```

## Configuration

1. **Create a `.env` file** in the root directory and add the following environment variables:
   ```env
   MONGO_URI="mongodb+srv://host:{your Database}.mongodb.net/"
   ```

2. **Ensure MongoDB is running**:
   - Start the MongoDB server if it is not already running.

## Running the Application

1. **Start the Flask application**:
   ```sh
   python MainWebapp/FlaskRegLogin.py
   ```

2. **Access the application**:
   - Open your web browser and navigate to `http://localhost:5000`.

## Project Structure

```
latent-fingerprint-webapp/
├── MainWebapp/
│   ├── FlaskRegLogin.py
│   ├── templates/
│   │   ├── check_enrollment.html
│   │   ├── view_enrollment.html
│   │   ├── match_fingerprints.html
│   │   ├── main.html
│   │   └── ...
│   ├── static/
│   │   ├── css/
│   │   │   ├── tailwind.css
│   │   │   └── styles.css
│   │   └── ...
│   └── ...
├── sourceafis-project/
│   ├── src/
│   │   ├── main/
│   │   │   ├── java/
│   │   │   │   ├── com/
│   │   │   │   │   ├── example/
│   │   │   │   │   │   ├── App.java
│   │   │   │   │   │   ├── FingerprintMatching.java
│   │   │   │   │   │   └── ...
│   │   │   │   │   └── ...
│   │   │   └── ...
│   │   └── ...
│   ├── pom.xml
│   └── ...
├── test_folder/
│   ├── gradio_webapp_ver_3.py
│   └── ...
├── .env
├── requirements.txt
└── README.md
```

## Usage

### User Roles

- **Police and Investigator**: Can enroll fingerprints, verify fingerprints, and identify fingerprints.
- **Forensic Expertise**: Can review verification and identification requests.
- **Citizen**: Can enroll fingerprints.
- **Government Official**: Can manage users and view logs.

### Routes

- **Home**: `/`
- **Register**: `/register`
- **Login**: `/login`
- **Main Page**: `/main`
- **Enrollment**: `/enrollment`
- **Check Enrollment**: `/check_enrollment`
- **View Enrollment**: `/view_enrollment/<user_id>`
- **View Approved Enrollments**: `/view_approved_enrollments`
- **Upload Latent Fingerprint**: `/upload_latent_fingerprint`
- **View Latent Fingerprints**: `/view_latent_fingerprints`
- **Enhance Latent Fingerprint**: `/enhance_latent_fingerprint/<fingerprint_id>`
- **Match Fingerprints**: `/match_fingerprints`
- **Manage Users**: `/manage_users`
- **View Logs**: `/view_logs`
- **Logout**: `/logout`

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
