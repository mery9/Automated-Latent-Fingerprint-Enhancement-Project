# Latent Fingerprint Web Application

This project is a web application for managing latent fingerprints, user enrollments, and fingerprint matching. It is built using Flask for the backend, MongoDB for the database, and Gradio for the user interface.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [Usage](#usage)
- [License](#license)

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.10.6 (higher version may bugged)
- Java 11
- MongoDB
- Maven

## Installation

1. **Clone the repository**:
   ```sh
   git clone https://github.com/yourusername/latent-fingerprint-webapp.git
   cd latent-fingerprint-webapp
   ```

2. **Set up the Python environment**:
   ```sh
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**:
   ```sh
   pip install -r requirements.txt
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
