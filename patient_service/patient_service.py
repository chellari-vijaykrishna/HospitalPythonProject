from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import os
import requests

app = Flask(__name__, template_folder='../templates')

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database='patient_db',
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route("/patients")
def list_patients():
    return render_template("patients.html")

@app.route("/api/patients", methods=["GET"])
def get_patients():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients")
    patients = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(patients)

@app.route("/api/patients/<int:patient_id>", methods=["GET"])
def get_patient(patient_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patients WHERE id = %s", (patient_id,))
    patient = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if patient:
        return jsonify(patient)
    return jsonify({"error": "Patient not found"}), 404

@app.route("/api/patients", methods=["POST"])
def create_patient():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO patients (name, age, gender, phone, address, medical_history) VALUES (%s, %s, %s, %s, %s, %s)",
        (data['name'], data['age'], data['gender'], data['phone'], data.get('address', ''), data.get('medical_history', ''))
    )
    patient_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"id": patient_id, "message": "Patient created"}), 201

@app.route("/api/patients/<int:patient_id>", methods=["PUT"])
def update_patient(patient_id):
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE patients SET name=%s, age=%s, gender=%s, phone=%s, address=%s, medical_history=%s WHERE id=%s",
        (data['name'], data['age'], data['gender'], data['phone'], data.get('address', ''), data.get('medical_history', ''), patient_id)
    )
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Patient updated"})

@app.route("/api/patients/<int:patient_id>", methods=["DELETE"])
def delete_patient(patient_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute("DELETE FROM patients WHERE id = %s", (patient_id,))
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"message": "Patient deleted"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)