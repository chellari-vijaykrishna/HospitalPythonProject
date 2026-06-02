from flask import Flask, request, jsonify, render_template
import mysql.connector
from mysql.connector import Error
import os

app = Flask(__name__, template_folder='../templates')

DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')

def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database='doctor_db',
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route("/doctors")
def list_doctors():
    return render_template("doctors.html")

@app.route("/api/doctors", methods=["GET"])
def get_doctors():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(doctors)

@app.route("/api/doctors/<int:doctor_id>", methods=["GET"])
def get_doctor(doctor_id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors WHERE id = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.close()
    conn.close()
    
    if doctor:
        return jsonify(doctor)
    return jsonify({"error": "Doctor not found"}), 404

@app.route("/api/doctors", methods=["POST"])
def create_doctor():
    data = request.json
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO doctors (name, specialization, phone, email, qualification, experience_years, fee) VALUES (%s, %s, %s, %s, %s, %s, %s)",
        (data['name'], data['specialization'], data['phone'], data['email'], data['qualification'], data.get('experience_years', 0), data.get('fee', 0))
    )
    doctor_id = cursor.lastrowid
    conn.commit()
    cursor.close()
    conn.close()
    return jsonify({"id": doctor_id, "message": "Doctor created"}), 201

@app.route("/api/doctors/specialization/<string:specialization>", methods=["GET"])
def get_doctors_by_specialization(specialization):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "Database connection failed"}), 500
    
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM doctors WHERE specialization LIKE %s", (f'%{specialization}%',))
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(doctors)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=True)