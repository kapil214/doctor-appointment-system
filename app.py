from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import hashlib

# --- APP SETUP ---
app = Flask(__name__)
# A secret key is required for session management to keep user login state secure
app.secret_key = 'your_super_secret_key_for_dev'

# --- DATABASE HELPER FUNCTIONS ---

def create_connection():
    """Create and return a new database connection."""
    return sqlite3.connect('clinic.db')

def hash_password(password):
    """Hash a password for storing."""
    return hashlib.sha256(password.encode()).hexdigest()

def check_password(hashed_password, user_password):
    """Check a hashed password against a user-provided password."""
    return hashed_password == hashlib.sha256(user_password.encode()).hexdigest()

# --- AUTHENTICATION ROUTES ---

@app.route('/', methods=['GET', 'POST'])
def login():
    """Handles user login."""
    if 'user_id' in session: # If already logged in, redirect to appropriate dashboard
        role = session.get('role')
        if role == 'admin':
            return redirect(url_for('admin_dashboard'))
        elif role == 'doctor':
            return redirect(url_for('doctor_dashboard'))
        elif role == 'patient':
            return redirect(url_for('patient_dashboard'))
            
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, password, role FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()

        if user and check_password(user[1], password):
            # Login successful, store user info in the session
            session['user_id'] = user[0]
            session['username'] = username
            session['role'] = user[2]
            flash('Login successful!', 'success')
            
            # Redirect to the correct dashboard
            if session['role'] == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif session['role'] == 'doctor':
                return redirect(url_for('doctor_dashboard'))
            else:
                return redirect(url_for('patient_dashboard'))
        else:
            flash('Invalid username or password. Please try again.', 'error')
            
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handles new patient registration."""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        contact = request.form['contact']
        
        hashed_pass = hash_password(password)
        
        try:
            conn = create_connection()
            cursor = conn.cursor()
            # Create user entry
            cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'patient')", (username, hashed_pass))
            user_id = cursor.lastrowid
            # Create patient entry
            cursor.execute("INSERT INTO patients (user_id, full_name, contact_number) VALUES (?, ?, ?)", (user_id, full_name, contact))
            conn.commit()
            conn.close()
            
            flash('Registration successful! You can now log in.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('This username is already taken. Please choose another.', 'error')
        except sqlite3.Error as e:
            flash(f'An error occurred: {e}', 'error')
            
    return render_template('register.html')

@app.route('/logout')
def logout():
    """Logs the user out by clearing the session."""
    session.clear()
    flash('You have been logged out.', 'success')
    return redirect(url_for('login'))

# --- ADMIN ROUTES ---

@app.route('/admin/dashboard')
def admin_dashboard():
    # Security check: Ensure user is logged in and is an admin
    if 'user_id' not in session or session.get('role') != 'admin':
        flash('You must be logged in as an admin to view this page.', 'error')
        return redirect(url_for('login'))
        
    conn = create_connection()
    cursor = conn.cursor()
    
    # Fetch all doctors
    cursor.execute("SELECT id, full_name, specialization FROM doctors")
    doctors = cursor.fetchall()
    
    # Fetch all appointments
    query = """
        SELECT a.id, p.full_name, d.full_name, a.appointment_date, a.appointment_time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
    """
    cursor.execute(query)
    appointments = cursor.fetchall()
    conn.close()

    return render_template('admin_dashboard.html', doctors=doctors, appointments=appointments)

@app.route('/admin/add_doctor', methods=['POST'])
def add_doctor():
    if 'user_id' not in session or session.get('role') != 'admin':
        return redirect(url_for('login'))

    username = request.form['username']
    password = hash_password(request.form['password'])
    full_name = request.form['full_name']
    specialization = request.form['specialization']

    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, password, role) VALUES (?, ?, 'doctor')", (username, password))
        user_id = cursor.lastrowid
        cursor.execute("INSERT INTO doctors (user_id, full_name, specialization) VALUES (?, ?, ?)", (user_id, full_name, specialization))
        conn.commit()
        conn.close()
        flash(f"Doctor '{full_name}' added successfully.", 'success')
    except sqlite3.IntegrityError:
        flash('This username for the doctor is already taken.', 'error')
    except sqlite3.Error as e:
        flash(f'Database error: {e}', 'error')
        
    return redirect(url_for('admin_dashboard'))

# --- DOCTOR ROUTES ---

@app.route('/doctor/dashboard')
def doctor_dashboard():
    if 'user_id' not in session or session.get('role') != 'doctor':
        flash('You must be logged in as a doctor to view this page.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = create_connection()
    cursor = conn.cursor()
    
    query = """
        SELECT a.id, p.full_name, a.appointment_date, a.appointment_time, a.status
        FROM appointments a
        JOIN patients p ON a.patient_id = p.id
        JOIN doctors d ON a.doctor_id = d.id
        WHERE d.user_id = ?
    """
    cursor.execute(query, (user_id,))
    appointments = cursor.fetchall()
    conn.close()

    return render_template('doctor_dashboard.html', appointments=appointments)

# --- PATIENT ROUTES ---

@app.route('/patient/dashboard')
def patient_dashboard():
    if 'user_id' not in session or session.get('role') != 'patient':
        flash('You must be logged in as a patient to view this page.', 'error')
        return redirect(url_for('login'))

    user_id = session['user_id']
    conn = create_connection()
    cursor = conn.cursor()
    
    # Fetch doctors for booking form
    cursor.execute("SELECT id, full_name, specialization FROM doctors")
    doctors = cursor.fetchall()
    
    # Fetch patient's appointments
    query = """
        SELECT a.id, d.full_name, d.specialization, a.appointment_date, a.appointment_time, a.status
        FROM appointments a
        JOIN doctors d ON a.doctor_id = d.id
        JOIN patients p ON a.patient_id = p.id
        WHERE p.user_id = ?
    """
    cursor.execute(query, (user_id,))
    appointments = cursor.fetchall()
    conn.close()

    return render_template('patient_dashboard.html', appointments=appointments, doctors=doctors)

@app.route('/patient/book_appointment', methods=['POST'])
def book_appointment():
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('login'))

    user_id = session['user_id']
    doctor_id = request.form['doctor_id']
    date = request.form['date']
    time = request.form['time']

    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM patients WHERE user_id = ?", (user_id,))
        patient_id = cursor.fetchone()[0]
        
        cursor.execute("INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time) VALUES (?, ?, ?, ?)",
                       (patient_id, doctor_id, date, time))
        conn.commit()
        conn.close()
        flash('Appointment booked successfully!', 'success')
    except sqlite3.Error as e:
        flash(f'Could not book appointment. Error: {e}', 'error')

    return redirect(url_for('patient_dashboard'))

@app.route('/patient/cancel/<int:appointment_id>')
def cancel_appointment(appointment_id):
    if 'user_id' not in session or session.get('role') != 'patient':
        return redirect(url_for('login'))
        
    try:
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE appointments SET status = 'cancelled' WHERE id = ?", (appointment_id,))
        conn.commit()
        conn.close()
        flash('Appointment cancelled successfully.', 'success')
    except sqlite3.Error as e:
        flash(f'Error cancelling appointment: {e}', 'error')
        
    return redirect(url_for('patient_dashboard'))

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    # The debug=True option allows you to see errors in the browser and auto-reloads the server when you save changes.
    # Turn this off in a real production environment.
    app.run(debug=True)
