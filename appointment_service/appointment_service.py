from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import os
import requests

# Get the absolute path to the project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(PROJECT_ROOT, 'templates')

app = Flask(__name__, template_folder=TEMPLATE_DIR)

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')

PATIENT_URL = "http://patient_service:5002"
DOCTOR_URL = "http://doctor_service:5003"

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database='appointment_db',
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route("/appointments")
def list_appointments():
    return render_template("appointments.html")

@app.route("/api/appointments", methods=["GET"])
def get_appointments():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments ORDER BY appointment_date DESC")
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(appointments)

@app.route("/api/appointments/<int:appointment_id>", methods=["GET"])
def get_appointment(appointment_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments WHERE id = %s", (appointment_id,))
    appointment = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if appointment:
        return jsonify(appointment)
    return jsonify({"error": "Appointment not found"}), 404

@app.route("/api/appointments", methods=["POST"])
def create_appointment():
    data = request.json
    
    # Verify patient exists
    try:
        patient_res = requests.get(f"{PATIENT_URL}/api/patients/{data['patient_id']}")
        if patient_res.status_code != 200:
            return jsonify({"error": "Patient not found"}), 404
    except:
        return jsonify({"error": "Patient service unavailable"}), 503
    
    # Verify doctor exists
    try:
        doctor_res = requests.get(f"{DOCTOR_URL}/api/doctors/{data['doctor_id']}")
        if doctor_res.status_code != 200:
            return jsonify({"error": "Doctor not found"}), 404
    except:
        return jsonify({"error": "Doctor service unavailable"}), 503
    
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, symptoms) VALUES (%s, %s, %s, %s, %s)",
        (data['patient_id'], data['doctor_id'], data['appointment_date'], data.get('status', 'scheduled'), data.get('symptoms', ''))
    )
    appointment_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"id": appointment_id, "message": "Appointment created"}), 201

@app.route("/api/appointments/patient/<int:patient_id>", methods=["GET"])
def get_patient_appointments(patient_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments WHERE patient_id = %s ORDER BY appointment_date DESC", (patient_id,))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(appointments)

@app.route("/api/appointments/doctor/<int:doctor_id>", methods=["GET"])
def get_doctor_appointments(doctor_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM appointments WHERE doctor_id = %s ORDER BY appointment_date DESC", (doctor_id,))
    appointments = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(appointments)

@app.route("/api/appointments/<int:appointment_id>/status", methods=["PATCH"])
def update_appointment_status(appointment_id):
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE appointments SET status=%s WHERE id=%s",
        (data['status'], appointment_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Appointment status updated"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004, debug=True)
