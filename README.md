Doctor Appointment Management System
A full-stack web application built with Python and Flask that provides a seamless, role-based platform for managing medical appointments. This project demonstrates core software engineering principles including database management, user authentication, and RESTful application structure.

Project Overview
The Doctor Appointment Management System is designed to replace traditional, manual appointment booking with a streamlined, digital solution. It caters to three distinct user roles—Administrators, Doctors, and Patients—each with a dedicated dashboard and a specific set of permissions and functionalities. The primary goal of this project is to create an efficient, organized, and user-friendly environment for managing healthcare appointments, showcasing a practical application of backend logic and frontend user interface design.

For an interviewer, this project serves as a clear demonstration of my ability to:

Design and implement a multi-user, role-based system.

Develop a full-stack application from the database schema to the user interface.

Implement secure user authentication and session management.

Structure code in a clean, maintainable, and scalable way using a web framework.

Key Features
The application's functionality is segregated by user roles to ensure security and relevance.

👤 Admin Features
Centralized Dashboard: View all doctors, patients, and appointments in the system.

Doctor Management: Add new doctors to the system with their specialization and create their login credentials.

System Oversight: Monitor all scheduled and cancelled appointments to manage clinic workflow.

👨‍⚕️ Doctor Features
Personalized Dashboard: View a personalized schedule of all upcoming appointments.

Patient Information: See which patients are scheduled for specific time slots.

Appointment Status: Track the status of each appointment (e.g., booked, cancelled).

🧑 Patient Features
Secure Registration & Login: Patients can create an account and log in securely.

Appointment Booking: View a list of available doctors and their specializations to book a new appointment.

Appointment Management: View all personal upcoming appointments, with the option to cancel them.

Technical Architecture & Tech Stack
This application follows a standard client-server architecture. The backend, built with Flask, handles all business logic, database interactions, and authentication, while the frontend renders the user interface using HTML and CSS.

Backend: Python with the Flask micro-framework.

Why Flask? Flask was chosen for its simplicity, flexibility, and minimal boilerplate, making it ideal for building a well-structured, single-purpose application like this one.

Database: SQLite.

Why SQLite? As a lightweight, serverless, and self-contained database, SQLite is perfect for development and small-to-medium scale applications. It requires zero configuration and is conveniently included with Python.

Frontend: HTML5 with CSS3.

Templating is handled by Jinja2 (which comes with Flask) to dynamically render data from the backend.

Authentication:

Password Hashing: Passwords are never stored in plain text. They are securely hashed using the hashlib library (SHA-256).

Session Management: Flask's secure session handling is used to manage user login states across different pages and protect routes based on user roles.

Database Schema
The database is designed with four main tables to logically separate user data, roles, and appointments, using foreign keys to establish relationships.

-- Users Table: Stores login credentials and roles for all users.
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL,
    role TEXT NOT NULL
);

-- Doctors Table: Stores doctor-specific information, linked to a user account.
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    full_name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Patients Table: Stores patient-specific information, linked to a user account.
CREATE TABLE patients (
    id INTEGER PRIMARY KEY,
    user_id INTEGER,
    full_name TEXT NOT NULL,
    contact_number TEXT,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Appointments Table: The core table linking patients and doctors for a specific time.
CREATE TABLE appointments (
    id INTEGER PRIMARY KEY,
    patient_id INTEGER,
    doctor_id INTEGER,
    appointment_date TEXT NOT NULL,
    appointment_time TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'booked',
    FOREIGN KEY (patient_id) REFERENCES patients (id),
    FOREIGN KEY (doctor_id) REFERENCES doctors (id)
);

How to Set Up and Run This Project Locally
Follow these steps to get the application running on your local machine.

Clone the Repository

git clone [https://github.com/kapil214/doctor-appointment-system.git](https://github.com/kapil214/doctor-appointment-system.git)
cd doctor-appointment-system

Create a Virtual Environment (Recommended)

# For Windows
python -m venv venv
venv\Scripts\activate

# For macOS/Linux
python3 -m venv venv
source venv/bin/activate

Install Dependencies
The only external dependency is Flask.

pip install Flask

Initialize the Database
Run the setup script once to create the clinic.db file and the necessary tables.

python database_setup.py

This will also create a default admin account with the credentials:

Username: admin

Password: admin123

Run the Flask Application

flask --app app run


Future Enhancements
This project provides a solid foundation that can be extended with additional features:

[ ] Doctor Availability: Implement a system for doctors to specify their available time slots.

[ ] Email Notifications: Integrate an email service to send appointment confirmations and reminders.

[ ] AJAX Integration: Use JavaScript and AJAX to make booking and cancellation actions more dynamic without full page reloads.

[ ] Database Migration: Upgrade from SQLite to a more robust database like PostgreSQL for production environments.

[ ] Containerization: Create a Dockerfile to containerize the application for easy deployment.
