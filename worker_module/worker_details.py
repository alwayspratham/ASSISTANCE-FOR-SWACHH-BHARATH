import sqlite3
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from datetime import datetime

# Define the blueprint for the worker module
worker_module = Blueprint('worker_module', __name__, template_folder='templates')

# Path to the databases
staff_db_path = 'staffdatabase.db'  # Ensure this points to staff.db
database_db_path = 'database.db'  # Ensure this points to database.db
progress_db_path = 'progress.db'  # Path to the progress database

# Initialize the progress database
def init_progress_db():
    conn = sqlite3.connect(progress_db_path)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS visited_links')  # Drop the table if it exists
    cursor.execute('''CREATE TABLE IF NOT EXISTS visited_links (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT,
                        latitude REAL,
                        longitude REAL,
                        visited_at TEXT)''')
    conn.commit()
    conn.close()

# Call init_progress_db to ensure the database is initialized
init_progress_db()

# Worker Login Route
@worker_module.route('/login', methods=['GET', 'POST'])
def worker_login():
    if request.method == 'POST':
        username = request.form['name']
        password = request.form['password']

        # Connect to staff.db (which contains staff table)
        conn = sqlite3.connect(staff_db_path)
        cursor = conn.cursor()
        
        # Check if the worker exists in staff table with role='worker'
        cursor.execute("SELECT id FROM staff WHERE name = ? AND password = ? AND role = 'worker'", (username, password))
        worker = cursor.fetchone()
        
        conn.close()

        if worker:
            worker_id = worker[0]  # Assuming 'id' is the first column in the staff table
            # Store worker_id in the session
            session['worker_id'] = worker_id
            flash('Login successful!', 'success')
            return redirect(url_for('worker_module.worker_dashboard'))
        else:
            flash('Invalid credentials or not a worker. Please try again.', 'danger')

    return render_template('worker_login.html')

# Worker Dashboard Route
@worker_module.route('/worker/dashboard', methods=['GET', 'POST'])
def worker_dashboard():
    if 'worker_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('worker_module.worker_login'))

    # Handle POST request to mark visited links
    if request.method == 'POST':
        visited_ids = request.form.getlist('visited_ids')  # Get list of visited IDs
        if visited_ids:
            try:
                conn_progress = sqlite3.connect(progress_db_path)
                cursor_progress = conn_progress.cursor()
                conn_user = sqlite3.connect(database_db_path)
                cursor_user = conn_user.cursor()

                for link_id in visited_ids:
                    cursor_user.execute("SELECT name, latitude, longitude FROM user_data WHERE id = ?", (link_id,))
                    row = cursor_user.fetchone()
                    if row:
                        cursor_progress.execute(
                            "INSERT INTO visited_links (name, latitude, longitude, visited_at) VALUES (?, ?, ?, ?)", 
                            (row[0], row[1], row[2], datetime.now())
                        )
                        cursor_user.execute("DELETE FROM user_data WHERE id = ?", (link_id,))
                
                conn_progress.commit()
                conn_user.commit()
                flash("Visited links have been stored.", "success")
            except sqlite3.Error as e:
                flash(f"Error: {e}", "danger")
            finally:
                cursor_progress.close()
                cursor_user.close()
        
        return redirect(url_for('worker_module.worker_dashboard'))

    # Fetch all workers' data from user_data table in database.db
    try:
        conn = sqlite3.connect(database_db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, longitude, latitude FROM user_data")
        worker_data = cursor.fetchall()
        print("Fetched Worker Data:", worker_data)  # Debugging: Print fetched data
    except sqlite3.Error as e:
        print(f"Database Error: {e}")
        flash(f"Database Error: {e}", "danger")
        worker_data = []
    finally:
        conn.close()

    # If no data is found, show a flash message
    if not worker_data:
        flash("No data found in the database.", "info")

    return render_template('worker_dashboard.html', worker_data=worker_data)


# Worker Logout Route
@worker_module.route('/worker/logout')
def worker_logout():
    session.pop('worker_id', None)  # Remove worker_id from the session
    flash("Logged out successfully!", "info")
    return redirect(url_for('worker_module.worker_login'))