from flask import Flask, render_template, request, redirect, session, flash, jsonify
import mysql.connector
import math
import base64
from hashlib import sha256
from cryptography.fernet import Fernet
from cryptography.fernet import Fernet

app = Flask(__name__)
app.secret_key = "supersecretkey"

# --- Database connection ---
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",   # put your MySQL password
    database="hospital_management"
)
cursor = db.cursor(dictionary=True)

# Haversine function
def haversine(lat1, lon1, lat2, lon2):
    R = 6371000  # Radius of Earth in meters
    phi1 = math.radians(float(lat1))
    phi2 = math.radians(float(lat2))
    delta_phi = math.radians(float(lat2) - float(lat1))
    delta_lambda = math.radians(float(lon2) - float(lon1))
    a = (math.sin(delta_phi / 2) ** 2 +
         math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_type = request.form["user_type"]
        username_email = request.form["username_email"]
        password = request.form["password"]
        latitude = request.form.get("latitude")
        longitude = request.form.get("longitude")

        # --- Admin login ---
        if user_type == "admin":
            cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username_email, password))
            user = cursor.fetchone()
            if user:
                if latitude and longitude:
                    cursor.execute("UPDATE admin SET latitude=%s, longitude=%s WHERE id=%s",
                                   (latitude, longitude, user["id"]))
                    db.commit()
                session["user_type"] = "admin"
                session["user_id"] = user["id"]
                return redirect("/admin_dashboard")

        # --- Nurse login ---
        elif user_type == "nurse":
            cursor.execute("SELECT * FROM nurse WHERE email=%s AND password=%s", (username_email, password))
            user = cursor.fetchone()
            if user:
                session["user_type"] = "nurse"
                session["user_id"] = user["id"]
                return redirect("/nurse_dashboard")

        # --- Doctor login ---
        elif user_type == "doctor":
            cursor.execute("SELECT * FROM doctor WHERE email=%s AND password=%s", (username_email, password))
            user = cursor.fetchone()
            if user:
                # Get latest admin location
                cursor.execute("SELECT latitude, longitude FROM admin ORDER BY id DESC LIMIT 1")
                admin_loc = cursor.fetchone()

                if not admin_loc or not admin_loc["latitude"] or not admin_loc["longitude"]:
                    flash("Admin location not set! Doctor login restricted.")
                    return redirect("/")

                if latitude and longitude:
                    distance = haversine(latitude, longitude, admin_loc["latitude"], admin_loc["longitude"])
                    if distance <= 5:  # 5 meters allowed
                        # Update doctor's location in DB
                        cursor.execute(
                            "UPDATE doctor SET latitude=%s, longitude=%s WHERE id=%s",
                            (latitude, longitude, user["id"])
                        )
                        db.commit()

                        session["user_type"] = "doctor"
                        session["user_id"] = user["id"]
                        return redirect("/doctor_dashboard")
                    else:
                        flash("You are not within the allowed login area!")
                        return redirect("/")
                else:
                    flash("Latitude and longitude required for doctor login!")
                    return redirect("/")

        flash("Invalid credentials")
    return render_template("login.html")

# --- Logout ---
@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")

# --- Admin Dashboard ---
@app.route("/admin_dashboard")
def admin_dashboard():
    if session.get("user_type") != "admin":
        return redirect("/")
    return render_template("admin_dashboard.html")

# --- Add Patient ---
@app.route("/add_patient", methods=["GET", "POST"])
def add_patient():
    if session.get("user_type") != "admin":
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        age = request.form["age"]
        gender = request.form["gender"]
        email = request.form["email"]
        mobile = request.form["mobile"]
        cursor.execute("INSERT INTO patient(name, age, gender, email, mobile) VALUES (%s,%s,%s,%s,%s)",
                       (name, age, gender, email, mobile))
        db.commit()
        flash("Patient added successfully!")
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()
    return render_template("add_patient.html", patients=patients)

# --- Add Nurse ---
@app.route("/add_nurse", methods=["GET", "POST"])
def add_nurse():
    if session.get("user_type") != "admin":
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        mobile = request.form["mobile"]
        key = request.form["key"]

        cursor.execute(
            "INSERT INTO nurse(name,email,password,mobile,`key`) VALUES(%s,%s,%s,%s,%s)",
            (name, email, password, mobile, key)
        )
        db.commit()
        flash("Nurse added successfully!")

    cursor.execute("SELECT * FROM nurse")
    nurses = cursor.fetchall()
    return render_template("add_nurse.html", nurses=nurses)


# --- Add Doctor ---
@app.route("/add_doctor", methods=["GET", "POST"])
def add_doctor():
    if session.get("user_type") != "admin":
        return redirect("/")
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        password = request.form["password"]
        mobile = request.form["mobile"]
        specialist = request.form["specialist"]
        cursor.execute("INSERT INTO doctor(name,email,password,mobile,specialist) VALUES(%s,%s,%s,%s,%s)",
                       (name,email,password,mobile,specialist))
        db.commit()
        flash("Doctor added successfully!")
    cursor.execute("SELECT * FROM doctor")
    doctors = cursor.fetchall()
    return render_template("add_doctor.html", doctors=doctors)

# --- Allot Patient ---
@app.route("/allot_patient", methods=["GET", "POST"])
def allot_patient():
  

    # Fetch all patients and doctors for the dropdown
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()
    cursor.execute("SELECT * FROM doctor")
    doctors = cursor.fetchall()

    if request.method == "POST":
        patient_id = request.form['patient_id']
        doctor_id = request.form['doctor_id']

        cursor.execute("INSERT INTO allot_patient (patient_id, doctor_id) VALUES (%s,%s)", (patient_id, doctor_id))
        db.commit()
        flash("Patient allotted successfully!")
        return redirect("/allot_patient")

    # Fetch all allotments to display in table
    cursor.execute("""
        SELECT ap.id, p.name AS patient_name, d.name AS doctor_name, d.specialist
        FROM allot_patient ap
        JOIN patient p ON ap.patient_id = p.id
        JOIN doctor d ON ap.doctor_id = d.id
        ORDER BY ap.id DESC
    """)
    allotments = cursor.fetchall()

    return render_template("allot_patient.html", patients=patients, doctors=doctors, allotments=allotments)

# --- Nurse Dashboard ---
@app.route("/nurse_dashboard")
def nurse_dashboard():
    if session.get("user_type") != "nurse":
        return redirect("/")
    return render_template("nurse_dashboard.html")

# --- Add Report ---
@app.route("/add_report", methods=["GET","POST"])
def add_report():
    
    cursor.execute("SELECT * FROM patient")
    patients = cursor.fetchall()
    if request.method == "POST":
        patient_id = request.form["patient_id"]
        temperature = request.form["temperature"]
        pulse_rate = request.form["pulse_rate"]
        spo2 = request.form["spo2"]
        height_cm = request.form["height_cm"]
        weight_kg = request.form["weight_kg"]
        cursor.execute("""INSERT INTO report(patient_id, temperature, pulse_rate, spo2, height_cm, weight_kg)
                          VALUES (%s,%s,%s,%s,%s,%s)""",
                       (patient_id, temperature, pulse_rate, spo2, height_cm, weight_kg))
        db.commit()
        flash("Report added successfully!")
    cursor.execute("""SELECT r.id, p.name as patient_name, r.temperature, r.pulse_rate, r.spo2, r.height_cm, r.weight_kg
                      FROM report r JOIN patient p ON r.patient_id=p.id""")
    reports = cursor.fetchall()
    return render_template("add_report.html", patients=patients, reports=reports)

# # --- Doctor Dashboard (optional) ---
# @app.route("/doctor_dashboard")
# def doctor_dashboard():
#     if session.get("user_type") != "doctor":
#         return redirect("/")
#     # Doctor can view patients allotted to them (optional)
#     return "Doctor Dashboard Coming Soon"


# ---------------- ENCRYPT REPORT ----------------
@app.route('/encrypt_report/<int:report_id>', methods=['POST'])
def encrypt_report(report_id):
    if session.get("user_type") != "nurse":
        flash("You must log in as a nurse first.")
        return redirect("/login")

    nurse_id = session.get("user_id")

    # Fetch nurse key
    cursor.execute("SELECT `key` FROM nurse WHERE id=%s", (nurse_id,))
    nurse = cursor.fetchone()
    if not nurse or not nurse["key"]:
        flash("Encryption key not found for this nurse!")
        return redirect("/add_report")

    nurse_key = nurse["key"]
    derived_key = base64.urlsafe_b64encode(sha256(nurse_key.encode()).digest())
    fernet = Fernet(derived_key)

    # Fetch report
    cursor.execute("SELECT * FROM report WHERE id=%s", (report_id,))
    report = cursor.fetchone()
    if not report:
        flash("Report not found!")
        return redirect("/add_report")

    # Encrypt data
    enc_temperature = fernet.encrypt(report["temperature"].encode()).decode()
    enc_pulse_rate = fernet.encrypt(report["pulse_rate"].encode()).decode()
    enc_spo2 = fernet.encrypt(report["spo2"].encode()).decode()
    enc_height_cm = fernet.encrypt(report["height_cm"].encode()).decode()
    enc_weight_kg = fernet.encrypt(report["weight_kg"].encode()).decode()

    # Store encrypted report
    cursor.execute("""
        INSERT INTO report_enc (report_id, nurse_id, enc_temperature, enc_pulse_rate, enc_spo2, enc_height_cm, enc_weight_kg)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, (report_id, nurse_id, enc_temperature, enc_pulse_rate, enc_spo2, enc_height_cm, enc_weight_kg))
    db.commit()

    flash("Report encrypted and stored successfully!")
    return redirect("/add_report")
# --- View Encrypted Data as stored in report_enc ---
@app.route("/view_report_enc_table")
def view_report_enc_table():
    if session.get("user_type") != "nurse":
        flash("You must log in as a nurse first.")
        return redirect("/")

    nurse_id = session.get("user_id")

    # Fetch all encrypted reports for this nurse
    cursor.execute("""
        SELECT re.id, p.name as patient_name, re.enc_temperature, re.enc_pulse_rate, 
               re.enc_spo2, re.enc_height_cm, re.enc_weight_kg
        FROM report_enc re
        JOIN report r ON re.report_id = r.id
        JOIN patient p ON r.patient_id = p.id
        WHERE re.nurse_id=%s
        ORDER BY re.id DESC
    """, (nurse_id,))
    enc_reports = cursor.fetchall()

    return render_template("view_report_enc_table.html", reports=enc_reports)
# --- Doctor Dashboard ---
@app.route("/doctor_dashboard")
def doctor_dashboard():
    if session.get("user_type") != "doctor":
        return redirect("/")
    return render_template("doctor_dashboard.html")

# --- View Allotted Patients for Doctor ---
@app.route("/doctor/view_allotted_patients")
def doctor_view_allotted_patients():
    if session.get("user_type") != "doctor":
        return redirect("/")

    doctor_id = session.get("user_id")

    # Fetch all patients allotted to this doctor
    cursor.execute("""
        SELECT p.id, p.name, p.age, p.gender, p.email, p.mobile
        FROM allot_patient ap
        JOIN patient p ON ap.patient_id = p.id
        WHERE ap.doctor_id = %s
        ORDER BY ap.id DESC
    """, (doctor_id,))
    patients = cursor.fetchall()

    return render_template("doctor_allotted_patients.html", patients=patients)
 
# --- View Encrypted Reports ---
@app.route("/doctor/view_encrypted_reports")
def doctor_view_encrypted_reports():
    if session.get("user_type") != "doctor":
        return redirect("/")

    doctor_id = session.get("user_id")

    # Fetch unique encrypted reports allotted to this doctor
    cursor.execute("""
        SELECT re.id as report_enc_id, r.id as report_id, p.name as patient_name,
               re.enc_temperature, re.enc_pulse_rate, re.enc_spo2, re.enc_height_cm, re.enc_weight_kg, n.key as nurse_key
        FROM report_enc re
        JOIN report r ON re.report_id = r.id
        JOIN patient p ON r.patient_id = p.id
        JOIN nurse n ON re.nurse_id = n.id
        WHERE re.id IN (
            SELECT re2.id
            FROM report_enc re2
            JOIN report r2 ON re2.report_id = r2.id
            JOIN allot_patient ap ON r2.patient_id = ap.patient_id
            WHERE ap.doctor_id = %s
        )
        ORDER BY re.id DESC
    """, (doctor_id,))
    reports = cursor.fetchall()
    return render_template("doctor_view_reports.html", reports=reports)

# --- Decrypt particular report ---
@app.route("/doctor/decrypt_report", methods=["POST"])
def doctor_decrypt_report():
    if session.get("user_type") != "doctor":
        return jsonify({"status":"error","msg":"Unauthorized"}), 403

    data = request.get_json()
    report_enc_id = data.get("report_enc_id")
    entered_key = data.get("key")

    # Fetch the encrypted report and nurse key
    cursor.execute("""
        SELECT re.*, n.key as nurse_key
        FROM report_enc re
        JOIN nurse n ON re.nurse_id = n.id
        WHERE re.id=%s
    """, (report_enc_id,))
    report_enc = cursor.fetchone()
    if not report_enc:
        return jsonify({"status":"error","msg":"Report not found"})

    nurse_key = report_enc["nurse_key"]

    if entered_key != nurse_key:
        return jsonify({"status":"error","msg":"Invalid key"})

    # Generate fernet key and decrypt
    derived_key = base64.urlsafe_b64encode(sha256(nurse_key.encode()).digest())
    fernet = Fernet(derived_key)

    decrypted_report = {
        "temperature": fernet.decrypt(report_enc["enc_temperature"].encode()).decode(),
        "pulse_rate": fernet.decrypt(report_enc["enc_pulse_rate"].encode()).decode(),
        "spo2": fernet.decrypt(report_enc["enc_spo2"].encode()).decode(),
        "height_cm": fernet.decrypt(report_enc["enc_height_cm"].encode()).decode(),
        "weight_kg": fernet.decrypt(report_enc["enc_weight_kg"].encode()).decode()
    }

    return jsonify({"status":"success","report":decrypted_report})
if __name__ == "__main__":
    app.run(debug=True)
