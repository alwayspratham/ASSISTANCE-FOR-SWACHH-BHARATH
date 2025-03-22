from flask import Flask, render_template, request, flash, redirect, url_for
from flask import Flask, request, jsonify
from shapely.geometry import shape, Point
import geopandas as gpd
import json


from utils.gis_utils import get_ward

 
from user_module.user_routes import user_blueprint  # User module
from staff_module.staff_details import staff_module  # Staff module
from worker_module.worker_details import worker_module  # Worker module

def register_blueprints(app):
    app.register_blueprint(user_blueprint, url_prefix='/user_module')  # User module
    app.register_blueprint(staff_module, url_prefix='/staff')  # Staff module
    app.register_blueprint(worker_module, url_prefix='/worker')  # Worker module
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session management (important for security)

# Register the blueprints with the appropriate URL prefixes
register_blueprints(app)

@app.route('/')
def index():
    # The home route renders the index page
    return render_template('index.html')

# About Us Page
@app.route('/about_us')
def about_us():
    return render_template('about_us.html')

# Feedback Page
@app.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        message = request.form.get('message')

        # Here, you can store the feedback in the database if needed
        # Example: save_to_database(name, message)

        flash('Thanks for your response!', 'success')
        return redirect(url_for('index'))

    return render_template('feedback.html')

# Enquiry Page
@app.route('/enquiry', methods=['GET', 'POST'])
def enquiry():
    if request.method == 'POST':
        name = request.form.get('name')
        contact = request.form.get('contact')
        query = request.form.get('query')

        # Here, you can store the enquiry in the database if needed
        # Example: save_to_database(name, contact, query)

        flash('Thanks for your enquiry! We will get back to you soon.', 'success')
        return redirect(url_for('index'))

    return render_template('enquiry.html')



geojson_file = "wards.geojson"
wards_gdf = gpd.read_file(geojson_file)
@app.route("/get_ward")
def get_ward():
    try:
        lat = float(request.args.get("lat"))
        lon = float(request.args.get("lon"))

        point = Point(lon, lat)  # Convert to a Shapely Point

        print(f"📍 Checking for location: ({lon}, {lat})")  # Debugging output

        for _, row in wards_gdf.iterrows():
            print(f"🔍 Checking Ward: {row['NAME']} with geometry: {row['geometry']}")  # Debugging output
            if row["geometry"].intersects(point):
                ward_name = row["NAME"]  # Corrected line
                print(f"✅ Found Ward: {ward_name}")  # Debugging output
                return jsonify({"ward_name": ward_name})

        print("🚨 No matching ward found")
        return jsonify({"error": "Ward not found"}), 404  # Return 404 if no ward found

    except Exception as e:
        print(f"🚨 Error in get_ward: {e}")
        return jsonify({"error": "Internal Server Error"}), 500
if __name__ == '__main__':
    app.run(debug=True)