-- Create multiple databases
CREATE DATABASE IF NOT EXISTS auth_db;
CREATE DATABASE IF NOT EXISTS patient_db;
CREATE DATABASE IF NOT EXISTS doctor_db;
CREATE DATABASE IF NOT EXISTS appointment_db;

-- Use auth_db
USE auth_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);

INSERT INTO users (email, password, role) VALUES 
('admin@hospital.com', SHA2('admin123', 256), 'admin'),
('doctor@hospital.com', SHA2('doctor123', 256), 'doctor'),
('patient@hospital.com', SHA2('patient123', 256), 'patient');

-- Use patient_db
USE patient_db;

CREATE TABLE IF NOT EXISTS patients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    age INT,
    gender VARCHAR(10),
    phone VARCHAR(50),
    address TEXT,
    medical_history TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_patients_name ON patients(name);
CREATE INDEX idx_patients_phone ON patients(phone);

INSERT INTO patients (name, age, gender, phone, address, medical_history) VALUES 
('John Doe', 35, 'Male', '1234567890', '123 Main St, City', 'None'),
('Jane Smith', 28, 'Female', '0987654321', '456 Oak Ave, Town', 'Allergic to penicillin'),
('Bob Wilson', 45, 'Male', '5551234567', '789 Pine St, Village', 'Diabetes');

-- Use doctor_db
USE doctor_db;

CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    specialization VARCHAR(255),
    phone VARCHAR(50),
    email VARCHAR(255) UNIQUE,
    qualification TEXT,
    experience_years INT DEFAULT 0,
    fee DECIMAL(10,2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_doctors_specialization ON doctors(specialization);
CREATE INDEX idx_doctors_email ON doctors(email);

INSERT INTO doctors (name, specialization, phone, email, qualification, experience_years, fee) VALUES 
('Dr. Sarah Johnson', 'Cardiology', '5550100', 'sarah.johnson@hospital.com', 'MD, PhD', 12, 150.00),
('Dr. Michael Chen', 'Pediatrics', '5550101', 'michael.chen@hospital.com', 'MD', 8, 120.00),
('Dr. Emily Rodriguez', 'Neurology', '5550102', 'emily.rodriguez@hospital.com', 'MD, MS', 15, 200.00),
('Dr. David Kim', 'Orthopedics', '5550103', 'david.kim@hospital.com', 'MD', 10, 175.00);

-- Use appointment_db
USE appointment_db;

CREATE TABLE IF NOT EXISTS appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT NOT NULL,
    doctor_id INT NOT NULL,
    appointment_date DATETIME NOT NULL,
    status VARCHAR(50) DEFAULT 'scheduled',
    symptoms TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_appointments_patient ON appointments(patient_id);
CREATE INDEX idx_appointments_doctor ON appointments(doctor_id);
CREATE INDEX idx_appointments_date ON appointments(appointment_date);
CREATE INDEX idx_appointments_status ON appointments(status);

INSERT INTO appointments (patient_id, doctor_id, appointment_date, status, symptoms) VALUES 
(1, 1, '2024-01-20 10:00:00', 'scheduled', 'Chest pain'),
(2, 2, '2024-01-20 11:30:00', 'scheduled', 'Fever and cough'),
(1, 3, '2024-01-21 14:00:00', 'confirmed', 'Headache');