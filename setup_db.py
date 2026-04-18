import mysql.connector

def setup_db():
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="hospital_db"
    )
    cursor = db.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS appointments (
            appointment_id INT AUTO_INCREMENT PRIMARY KEY,
            patient_id INT,
            doctor_id INT,
            appointment_date DATE,
            appointment_time TIME,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (patient_id) REFERENCES patients(patient_id) ON DELETE CASCADE,
            FOREIGN KEY (doctor_id) REFERENCES doctors(doctor_id) ON DELETE CASCADE
        )
    """)
    db.commit()
    db.close()
    print("Appointments table created successfully.")

if __name__ == "__main__":
    setup_db()
