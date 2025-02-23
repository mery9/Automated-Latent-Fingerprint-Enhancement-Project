
# System Documentation for Automated Latent Fingerprint Enhancement System

## Table of Contents
1. [Introduction](#introduction)
2. [System Architecture](#system-architecture)
3. [Database Schema](#database-schema)
4. [API Endpoints](#api-endpoints)
5. [User Roles and Permissions](#user-roles-and-permissions)
6. [Frontend Components](#frontend-components)
7. [Backend Components](#backend-components)
8. [Deployment](#deployment)
9. [Conclusion](#conclusion)

## Introduction
The Automated Latent Fingerprint Enhancement System is designed to enhance, match, and manage latent fingerprints. The system supports various user roles, including Citizens, Police and Investigators, Forensic Experts, and Government Officials, each with specific functionalities and permissions.

## System Architecture
The system is built using the Flask framework for the backend and MongoDB for the database. The frontend is designed using HTML, CSS, and Tailwind CSS for styling.

### Components
- **Frontend**: HTML, CSS, Tailwind CSS
- **Backend**: Flask, Python
- **Database**: MongoDB, GridFS for file storage

## Database Schema
The database consists of several collections to store user data, enrollments, logs, images, and results.

### Collections
- **users**: Stores user information and roles.
- **enrollments**: Stores enrollment data, including fingerprints.
- **logs**: Stores logs of user actions.
- **images**: Stores images using GridFS.
- **latent_fingerprints_images**: Stores latent fingerprint images.
- **identification_results**: Stores results of fingerprint identification.
- **enhanced_images**: Stores enhanced fingerprint images.

## API Endpoints
The system provides various API endpoints for different functionalities.

### Authentication
- **`/register`**: User registration
- **`/login`**: User login
- **`/logout`**: User logout

### User Management
- **`/manage_users`**: Manage users (Government Official role)

### Enrollment
- **`/enrollment`**: Enroll fingerprints (Citizen, Police and Investigator roles)
- **`/check_enrollment`**: Check and update enrollment (Police and Investigator role)
- **`/view_approved_enrollments`**: View approved enrollments (Police and Investigator role)

### Fingerprint Processing
- **`/enhance_fingerprint`**: Enhance fingerprints (Forensic Expertise role)
- **`/match_fingerprints`**: Match fingerprints (Forensic Expertise role)
- **`/identify_fingerprints`**: Identify fingerprints (Forensic Expertise role)

### Logs
- **`/view_logs`**: View system logs (Government Official role)
- **`/view_enhancement_logs`**: View enhancement logs (Forensic Expertise role)
- **`/view_identification_logs`**: View identification logs (Forensic Expertise role)

## User Roles and Permissions
The system supports multiple user roles, each with specific permissions.

### Roles
- **Citizen**: Can enroll fingerprints.
- **Police and Investigator**: Can enroll fingerprints, check and update enrollments, view approved enrollments.
- **Forensic Expertise**: Can enhance, match, and identify fingerprints.
- **Government Official**: Can manage users and view system logs.

## Frontend Components
The frontend consists of various HTML templates styled with Tailwind CSS.

### Key Templates
- **`main.html`**: Main page for logged-in users.
- **`register.html`**: User registration page.
- **`login.html`**: User login page.
- **`enrollment.html`**: Enrollment form.
- **`manage_users.html`**: Manage users page.
- **`view_approved_enrollments.html`**: View approved enrollments page.
- **`check_enrollment.html`**: Check and update enrollment page.
- **`enhance_fingerprint.html`**: Enhance fingerprint page.
- **`match_fingerprints.html`**: Match fingerprints page.
- **`identify_fingerprints.html`**: Identify fingerprints page.

## Backend Components
The backend is built using Flask and includes various routes and utility functions.

### Key Routes
- **`/register`**: Handles user registration.
- **`/login`**: Handles user login.
- **`/logout`**: Handles user logout.
- **`/enrollment`**: Handles fingerprint enrollment.
- **`/check_enrollment`**: Handles checking and updating enrollments.
- **`/view_approved_enrollments`**: Handles viewing approved enrollments.
- **`/enhance_fingerprint`**: Handles fingerprint enhancement.
- **`/match_fingerprints`**: Handles fingerprint matching.
- **`/identify_fingerprints`**: Handles fingerprint identification.
- **`/manage_users`**: Handles user management.
- **`/view_logs`**: Handles viewing system logs.
- **`/view_enhancement_logs`**: Handles viewing enhancement logs.
- **`/view_identification_logs`**: Handles viewing identification logs.

### Utility Functions
- **`log_action`**: Logs user actions.
- **`save_photo`**: Saves uploaded photos to GridFS.
- **`calculate_shard_number`**: Calculates shard number for user ID.
- **`get_next_sequence_number`**: Gets the next sequence number for enrollments.

## Deployment
The system can be deployed on any server that supports Flask and MongoDB. Ensure that the environment variables are set correctly and the necessary dependencies are installed.

### Steps
1. Clone the repository.
2. Set up the environment variables in a `.env` file.
3. Install the required dependencies using `pip install -r requirements.txt`.
4. Run the Flask application using `python FlaskRegLogin.py`.

## Conclusion
This system documentation provides an overview of the Automated Latent Fingerprint Enhancement System, including its architecture, database schema, API endpoints, user roles, frontend and backend components, and deployment steps. This documentation serves as a guide for understanding and maintaining the system.

