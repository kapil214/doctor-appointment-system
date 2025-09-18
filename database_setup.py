import sqlite3
import hashlib

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def create_connection():
    """Create a database connection to a SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('clinic.db')
        print(f"SQLite version: {sqlite3.sqlite_version}")
        print("Database connection successful.")
        return conn
    except sqlite3.Error as e:
        print(e)
    return conn

def create_tables(conn):
    """Create tables for the database."""
    try:
        cursor = conn.cursor()
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                role TEXT NOT NULL CHECK(role IN ('admin', 'doctor', 'patient'))
            );
        """)
        
        # Doctors table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                specialization TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)
        
        # Patients table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                full_name TEXT NOT NULL,
                contact_number TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            );
        """)

        # Appointments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS appointments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                patient_id INTEGER NOT NULL,
                doctor_id INTEGER NOT NULL,
                appointment_date TEXT NOT NULL,
                appointment_time TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'booked' CHECK(status IN ('booked', 'cancelled')),
                FOREIGN KEY (patient_id) REFERENCES patients (id),
                FOREIGN KEY (doctor_id) REFERENCES doctors (id)
            );
        """)
        print("Tables created successfully.")
        conn.commit()
    except sqlite3.Error as e:
        print(f"Error creating tables: {e}")

def create_default_admin(conn):
    """Create a default admin user if one doesn't exist."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM users WHERE username = 'admin'")
        if not cursor.fetchone():
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
                           ('admin', hash_password('admin123'), 'admin'))
            conn.commit()
            print("Default admin account created with username 'admin' and password 'admin123'")
        else:
            print("Admin account already exists.")
    except sqlite3.Error as e:
        print(f"Error creating admin: {e}")

if __name__ == '__main__':
    connection = create_connection()
    if connection:
        create_tables(connection)
        create_default_admin(connection)
        connection.close()
        print("Database setup complete.")
