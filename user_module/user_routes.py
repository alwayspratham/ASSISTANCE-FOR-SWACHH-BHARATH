from flask import Blueprint, render_template, request, redirect, url_for, flash, send_file
import sqlite3
import os
import io

# Define the blueprint
user_blueprint = Blueprint('user_module', __name__, template_folder='templates', static_folder='static')
DATABASE = 'database.db'

# Initialize the database
def init_db():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        email TEXT NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        image BLOB)''')  # Store images as BLOBs
    conn.commit()
    conn.close()

init_db()

# Convert image file to binary
def convert_to_binary(file):
    return file.read()

# Route for user form
@user_blueprint.route('/', methods=['GET', 'POST'])
def user_form():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        image = request.files.get('image')

        # Validate inputs
        if not name or not email or not latitude or not longitude:
            flash("All fields except the image are required.", "warning")
            return redirect(url_for('user_module.user_form'))

        image_blob = convert_to_binary(image) if image and image.filename else None

        try:
            conn = sqlite3.connect(DATABASE)
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM user_data WHERE name = ? AND email = ? AND latitude = ? AND longitude = ?',
                           (name, email, latitude, longitude))
            existing_data = cursor.fetchone()

          
            
            cursor.execute('INSERT INTO user_data (name, email, latitude, longitude, image) VALUES (?, ?, ?, ?, ?)',
                               (name, email, float(latitude), float(longitude), image_blob))
            conn.commit()
            flash("Data has been successfully inserted into the database.", "success")
        except sqlite3.Error as e:
            flash(f"An error occurred: {e}", "danger")
        finally:
            conn.close()

        return redirect(url_for('user_module.user_form'))

    # Fetch all user data
    try:
        conn = sqlite3.connect(DATABASE)
        cursor = conn.cursor()
        cursor.execute('SELECT id, name, email, latitude, longitude FROM user_data')  # No images here
        user_data = cursor.fetchall()
    except sqlite3.Error as e:
        flash(f"Error fetching data: {e}", "danger")
        user_data = []
    finally:
        conn.close()

    return render_template('user_form.html', user_data=user_data)

# Route to fetch image from database
@user_blueprint.route('/get_image/<int:user_id>')
def get_image(user_id):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT image FROM user_data WHERE id = ?", (user_id,))
    data = cursor.fetchone()
    conn.close()
    
    if data and data[0]:
        return send_file(io.BytesIO(data[0]), mimetype='image/jpeg')
    return "No image found", 404
def citizen_data():
    """Fetch all data from the citizen database."""
    conn = sqlite3.connect(database='database.db')
    cursor = conn.cursor()
    
    # Fetch all data from the citizen table
    cursor.execute('SELECT id, name, email, latitude, longitude FROM user_data')
    
    citizen_data = cursor.fetchall()
    
    # Print data to the terminal
    for row in citizen_data:
        print(row)
    
    conn.close()