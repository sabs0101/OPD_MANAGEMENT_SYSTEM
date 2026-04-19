from flask import Flask, render_template, request, redirect, session, jsonify, Response
import mysql.connector
import re
import os

app = Flask(__name__)
app.secret_key = "secret123"


# ✅ ALWAYS CREATE NEW DB CONNECTION
def get_db():
    return mysql.connector.connect(
    host=os.getenv("MYSQLHOST"),
    user=os.getenv("MYSQLUSER"),
    password=os.getenv("MYSQLPASSWORD"),
    database=os.getenv("MYSQLDATABASE"),
    port=int(os.getenv("MYSQLPORT"))
    )


# ---------------- LOGIN ----------------
@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":
        u = request.form.get("username")
        p = request.form.get("password")

        db = get_db()
        cursor = db.cursor(dictionary=True, buffered=True)

        cursor.execute(
            "SELECT * FROM admins WHERE username=%s AND password=%s",
            (u, p)
        )

        admin = cursor.fetchone()
        db.close()

        if admin:
            session["admin"] = u
            return redirect("/")

        return render_template("login.html", error="Invalid Login")

    return render_template("login.html")


# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/login")


# ---------------- DASHBOARD ----------------
@app.route("/")
def dashboard():

    if "admin" not in session:
        return redirect("/login")

    return render_template("dashboard.html")


# ---------------- COUNTS API ----------------
@app.route("/api/counts")
def counts():

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT COUNT(*) as total FROM patients")
    patients = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM doctors")
    doctors = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as total FROM nurses")
    nurses = cursor.fetchone()["total"]

    db.close()

    return jsonify({
        "patients": patients,
        "doctors": doctors,
        "nurses": nurses
    })


# ---------------- PATIENT API ----------------
@app.route("/api/patients")
def api_patients():

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    cursor.execute("SELECT * FROM patients ORDER BY patient_id DESC")
    data = cursor.fetchall()

    db.close()

    return jsonify(data)


# ---------------- ADD PATIENT ----------------
@app.route("/patients/new", methods=["GET", "POST"])
def new_patient():

    if "admin" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    if request.method == "POST":

        name = request.form.get("name")
        age = int(request.form.get("age"))
        gender = request.form.get("gender")
        phone = request.form.get("phone")
        family = request.form.get("family")
        disease = request.form.get("disease")
        doctor = request.form.get("doctor")
        nurse = request.form.get("nurse")

        # ✅ VALIDATION
        if not re.match("^[A-Za-z ]+$", name):
            return "Invalid Name"

        if age <= 0 or age > 120:
            return "Invalid Age"

        if not re.match("^[0-9]{10}$", phone):
            return "Invalid Phone"

        cursor.execute("""
        INSERT INTO patients
        (name, age, gender, phone, family, disease, doctor, nurse)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
        """, (name, age, gender, phone, family, disease, doctor, nurse))

        db.commit()
        db.close()

        return redirect("/")

    # GET request
    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    cursor.execute("SELECT * FROM nurses")
    nurses = cursor.fetchall()

    db.close()

    return render_template("patient_form.html",
                           doctors=doctors,
                           nurses=nurses)


# ---------------- EDIT PATIENT ----------------
@app.route("/patients/edit/<int:id>", methods=["GET", "POST"])
def edit_patient(id):

    if "admin" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    if request.method == "POST":

        name = request.form.get("name")
        age = int(request.form.get("age"))
        gender = request.form.get("gender")
        phone = request.form.get("phone")
        family = request.form.get("family")
        disease = request.form.get("disease")
        doctor = request.form.get("doctor")
        nurse = request.form.get("nurse")

        cursor.execute("""
        UPDATE patients
        SET name=%s, age=%s, gender=%s, phone=%s,
        family=%s, disease=%s, doctor=%s, nurse=%s
        WHERE patient_id=%s
        """, (name, age, gender, phone, family, disease, doctor, nurse, id))

        db.commit()
        db.close()

        return redirect("/")

    # GET
    cursor.execute("SELECT * FROM patients WHERE patient_id=%s", (id,))
    patient = cursor.fetchone()

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    cursor.execute("SELECT * FROM nurses")
    nurses = cursor.fetchall()

    db.close()

    return render_template("edit_patient.html",
                           patient=patient,
                           doctors=doctors,
                           nurses=nurses)


# ---------------- DELETE PATIENT ----------------
@app.route("/patients/delete/<int:id>")
def delete_patient(id):
    if "admin" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("DELETE FROM patients WHERE patient_id=%s", (id,))
    db.commit()
    db.close()

    return redirect("/")


# ---------------- DELETE DOCTOR ----------------
@app.route("/doctors/delete/<int:id>")
def delete_doctor(id):
    if "admin" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("DELETE FROM doctors WHERE doctor_id=%s", (id,))
    db.commit()
    db.close()

    return redirect("/doctors")


# ---------------- DELETE NURSE ----------------
@app.route("/nurses/delete/<int:id>")
def delete_nurse(id):
    if "admin" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("DELETE FROM nurses WHERE nurse_id=%s", (id,))
    db.commit()
    db.close()

    return redirect("/nurses")


# ---------------- DOCTORS ----------------
@app.route("/doctors", methods=["GET", "POST"])
def doctors():

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    if request.method == "POST":
        name = request.form.get("name")

        cursor.execute("INSERT INTO doctors(name) VALUES(%s)", (name,))
        db.commit()

    cursor.execute("SELECT * FROM doctors")
    doctors = cursor.fetchall()

    db.close()

    return render_template("doctors.html", doctors=doctors)


# ---------------- NURSES ----------------
@app.route("/nurses", methods=["GET", "POST"])
def nurses():

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    if request.method == "POST":
        name = request.form.get("name")

        cursor.execute("INSERT INTO nurses(name) VALUES(%s)", (name,))
        db.commit()

    cursor.execute("SELECT * FROM nurses")
    nurses = cursor.fetchall()

    db.close()

    return render_template("nurses.html", nurses=nurses)


# ---------------- APPOINTMENTS ----------------
@app.route("/appointments")
def appointments():
    if "admin" not in session:
        return redirect("/login")
    
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)
    
    query = """
    SELECT a.appointment_id, a.appointment_date, a.appointment_time,
           p.name AS patient_name, d.name AS doctor_name
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    ORDER BY a.appointment_date DESC, a.appointment_time DESC
    """
    cursor.execute(query)
    appointments = cursor.fetchall()
    db.close()
    
    return render_template("appointments.html", appointments=appointments)


@app.route("/appointments/new", methods=["GET", "POST"])
def new_appointment():
    if "admin" not in session:
        return redirect("/login")
    
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)
    
    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        doctor_id = request.form.get("doctor_id")
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")
        
        from datetime import datetime
        if datetime.strptime(appointment_date, "%Y-%m-%d").date() < datetime.now().date():
            return "Cannot book an appointment in the past.", 400
        
        cursor.execute("""
        INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time)
        VALUES (%s, %s, %s, %s)
        """, (patient_id, doctor_id, appointment_date, appointment_time))
        db.commit()
        db.close()
        return redirect("/appointments")
        
    cursor.execute("SELECT patient_id, name FROM patients")
    patients = cursor.fetchall()
    
    cursor.execute("SELECT doctor_id, name FROM doctors")
    doctors = cursor.fetchall()
    db.close()
    
    return render_template("appointment_form.html", patients=patients, doctors=doctors)


@app.route("/appointments/download/<int:id>")
def download_appointment(id):
    if "admin" not in session:
        return redirect("/login")
        
    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)
    
    query = """
    SELECT a.appointment_id, a.appointment_date, a.appointment_time,
           p.name AS patient_name, p.phone AS patient_phone, d.name AS doctor_name
    FROM appointments a
    JOIN patients p ON a.patient_id = p.patient_id
    JOIN doctors d ON a.doctor_id = d.doctor_id
    WHERE a.appointment_id = %s
    """
    cursor.execute(query, (id,))
    apt = cursor.fetchone()
    db.close()
    
    if not apt:
        return "Appointment not found", 404
        
    from reportlab.pdfgen import canvas
    from io import BytesIO
    
    buffer = BytesIO()
    p = canvas.Canvas(buffer)
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, 800, "--- APPOINTMENT DETAILS ---")
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"ID: {apt['appointment_id']}")
    p.drawString(100, 750, f"Patient: {apt['patient_name']}")
    p.drawString(100, 730, f"Phone: {apt['patient_phone']}")
    p.drawString(100, 710, f"Doctor: {apt['doctor_name']}")
    p.drawString(100, 690, f"Date: {apt['appointment_date']}")
    p.drawString(100, 670, f"Time: {apt['appointment_time']}")
    p.drawString(100, 650, "--------------------------------------------------------")
    p.drawString(100, 630, "Please arrive 15 minutes before the scheduled time.")
    p.showPage()
    p.save()
    
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return Response(pdf_bytes, 
                    mimetype="application/pdf",
                    headers={"Content-Disposition": f"attachment;filename=appointment_{id}.pdf"})

# ---------------- EDIT APPOINTMENT ----------------
@app.route("/appointments/edit/<int:id>", methods=["GET", "POST"])
def edit_appointment(id):
    if "admin" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(dictionary=True, buffered=True)

    if request.method == "POST":
        patient_id = request.form.get("patient_id")
        doctor_id = request.form.get("doctor_id")
        appointment_date = request.form.get("appointment_date")
        appointment_time = request.form.get("appointment_time")

        cursor.execute("""
        UPDATE appointments
        SET patient_id=%s, doctor_id=%s, appointment_date=%s, appointment_time=%s
        WHERE appointment_id=%s
        """, (patient_id, doctor_id, appointment_date, appointment_time, id))

        db.commit()
        db.close()
        return redirect("/appointments")

    # GET – load existing appointment + dropdowns
    cursor.execute("SELECT * FROM appointments WHERE appointment_id=%s", (id,))
    appointment = cursor.fetchone()

    cursor.execute("SELECT patient_id, name FROM patients")
    patients = cursor.fetchall()

    cursor.execute("SELECT doctor_id, name FROM doctors")
    doctors = cursor.fetchall()

    db.close()

    return render_template("edit_appointment.html",
                           appointment=appointment,
                           patients=patients,
                           doctors=doctors)


# ---------------- DELETE APPOINTMENT ----------------
@app.route("/appointments/delete/<int:id>")
def delete_appointment(id):
    if "admin" not in session:
        return redirect("/login")

    db = get_db()
    cursor = db.cursor(buffered=True)
    cursor.execute("DELETE FROM appointments WHERE appointment_id=%s", (id,))
    db.commit()
    db.close()

    return redirect("/appointments")


# ---------------- RUN ----------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port = int(os.getenv("PORT", 5000)))

