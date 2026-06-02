from flask import Flask, render_template, request, redirect, url_for, session, flash
import mysql.connector
from mysql.connector import Error
import hashlib
import os

app = Flask(__name__, template_folder='../templates')
app.secret_key = "hospital_secret_key"

# Database configuration - Single database microservice
DB_HOST = os.environ.get('DB_HOST', 'db')
DB_USER = os.environ.get('DB_USER', 'root')
DB_PASSWORD = os.environ.get('DB_PASSWORD', 'root')

# Service URLs
PATIENT_URL = "http://patient_service:5002"
DOCTOR_URL = "http://doctor_service:5003"
APPOINTMENT_URL = "http://appointment_service:5004"

def get_db_connection(database):
    try:
        connection = mysql.connector.connect(
            host=DB_HOST,
            database=database,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None

@app.route("/")
def home():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("signin"))

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        role = request.form.get("role", "patient")
        
        conn = get_db_connection('auth_db')
        if not conn:
            flash("Database connection error", "danger")
            return render_template("signup.html")
        
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (email, password, role) VALUES (%s, %s, %s)",
                (email, password, role)
            )
            conn.commit()
            flash("Signup successful! Please sign in.", "success")
            return redirect(url_for("signin"))
        except Exception as e:
            conn.rollback()
            flash(f"Signup failed: {str(e)}", "danger")
        finally:
            cursor.close()
            conn.close()
    
    return render_template("signup.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        email = request.form["email"]
        password = hashlib.sha256(request.form["password"].encode()).hexdigest()
        
        conn = get_db_connection('auth_db')
        if not conn:
            flash("Database connection error", "danger")
            return render_template("signin.html")
        
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute(
            "SELECT * FROM users WHERE email = %s AND password = %s",
            (email, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if user:
            session["user_id"] = user["id"]
            session["user_email"] = user["email"]
            session["user_role"] = user["role"]
            flash("Signin successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid email or password", "danger")
    
    return render_template("signin.html")

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("signin"))
    return render_template("dashboard.html", role=session.get("user_role"))

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("signin"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)