import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import os

# Create Blueprint for the staff module
staff_module = Blueprint('staff_module', __name__, template_folder='templates')

# Define database paths within the project
staff_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'staffdatabase.db'))
progress_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'progress.db'))
citizen_db_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'database.db'))

# Function to initialize the staff database
def init_staff_db():
    conn = sqlite3.connect(staff_db_path)
    cursor = conn.cursor()

    # Create `staff` table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS staff (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL CHECK(role IN ('worker', 'admin'))
    )
    """)

    # Add default admin user if not exists
    cursor.execute("SELECT COUNT(*) FROM staff WHERE name = 'admin' AND role = 'admin'")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO staff (name, password, role) VALUES ('admin', 'admin123', 'admin')")

    conn.commit()
    conn.close()

# Function to initialize the progress database
def init_progress_db():
    conn = sqlite3.connect(progress_db_path)
    cursor = conn.cursor()

    # Create `assignments` table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS assignments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        worker_id INTEGER NOT NULL,
        location_id INTEGER NOT NULL,
        FOREIGN KEY(worker_id) REFERENCES staff(id),
        FOREIGN KEY(location_id) REFERENCES user_data(id)
    )
    """)

    conn.commit()
    conn.close()

# Initialize databases at startup
init_staff_db()
init_progress_db()

# Admin Login Route
@staff_module.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()  # Strip spaces
        password = request.form['password'].strip()  # Strip spaces

        # Connect to the database
        conn = sqlite3.connect(staff_db_path)
        cursor = conn.cursor()

        # Query for the user
        cursor.execute("SELECT * FROM staff WHERE name = ? AND password = ?", (username, password))
        user = cursor.fetchone()
        conn.close()

        if user:  # If user exists
            if user[3] == 'admin':
                session['user_id'] = user[0]  # Store user ID in session
                flash("Login successful!", "success")
                return redirect(url_for('staff_module.admin_dashboard'))
            else:
                flash("You are not authorized to access the admin dashboard.", "danger")
        else:
            flash("Invalid credentials, please try again.", "danger")

    return render_template('login.html')

# Admin Dashboard - View Staff
@staff_module.route('/admin_dashboard')
def admin_dashboard():
    """Fetch all staff except admins and display them on the admin dashboard."""
    conn = sqlite3.connect(staff_db_path)
    cursor = conn.cursor()
    
    # Exclude staff with role 'admin'
    cursor.execute("SELECT id, name, role FROM staff WHERE role != 'admin'") 
    staff_data = cursor.fetchall()
    conn.close()
    
    return render_template('admin_dashboard.html', staff_data=staff_data)

# Add Staff
@staff_module.route('/add_staff', methods=['POST'])
def add_new_staff():
    """Add a new staff member."""
    name = request.form['name']
    password = request.form['password']
    role = request.form['role']
    
    # Insert the new staff into the database
    conn = sqlite3.connect(staff_db_path)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO staff (name, password, role) VALUES (?, ?, ?)", (name, password, role))
    conn.commit()
    conn.close()

    flash("Staff member added successfully!", "success")
    return redirect(url_for('staff_module.admin_dashboard'))

# Delete Staff
@staff_module.route('/delete_staff/<int:staff_id>', methods=['POST'])
def remove_staff(staff_id):
    """Delete a staff member from the database."""
    conn = sqlite3.connect(staff_db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM staff WHERE id = ?", (staff_id,))
    conn.commit()
    conn.close()

    flash("Staff member deleted successfully!", "success")
    return redirect(url_for('staff_module.admin_dashboard'))

# Worker Details Route
@staff_module.route('/worker_details')
def worker_details():
    """Fetch all data from the visited_links table in the progress database."""
    conn = sqlite3.connect(progress_db_path)
    cursor = conn.cursor()
    
    # Fetch all data from the visited_links table
    cursor.execute("SELECT id, name, latitude, longitude, visited_at FROM visited_links")
    visited_links_data = cursor.fetchall()
    
    conn.close()
    
    return render_template('worker_details.html', visited_links_data=visited_links_data)

# Citizen Data Route
@staff_module.route('/citizen_data')
def citizen_data():
    """Fetch all data from the citizen database and list of workers."""
    conn = sqlite3.connect(citizen_db_path)
    cursor = conn.cursor()
    
    # Fetch all data from the citizen table
    cursor.execute('SELECT id, name, email, latitude, longitude FROM user_data')
    citizen_data = cursor.fetchall()
    
    # Fetch all workers
    conn = sqlite3.connect(staff_db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name FROM staff WHERE role = 'worker'")
    workers = cursor.fetchall()
    
    conn.close()
    
    return render_template('citizen_data.html', citizen_data=citizen_data, workers=workers)

# Assign Location Route
@staff_module.route('/assign_location', methods=['POST'])
def assign_location():
    """Assign a location to a worker and delete the location from the user_data table."""
    worker_id = request.form['worker_id']
    location_id = request.form['location_id']
    
    # Connect to the progress database
    conn = sqlite3.connect(progress_db_path)
    cursor = conn.cursor()
    
    # Insert the assignment into the database
    cursor.execute("INSERT INTO assignments (worker_id, location_id) VALUES (?, ?)", (worker_id, location_id))
    conn.commit()
    conn.close()
    
    # Connect to the citizen database to delete the assigned location
    conn = sqlite3.connect(citizen_db_path)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM user_data WHERE id = ?", (location_id,))
    conn.commit()
    conn.close()
    
    flash("Location assigned to worker and deleted successfully!", "success")
    return redirect(url_for('staff_module.citizen_data'))