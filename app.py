from flask import Flask, render_template, request, redirect, session, jsonify
import sqlite3
import os

app = Flask(__name__)
app.secret_key = "tech4life_admin_secret_key"

DATABASE = "tech4life.db"


def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def create_database():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS hospitals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            location TEXT NOT NULL,
            beds INTEGER DEFAULT 0,
            total_beds INTEGER DEFAULT 0,
            available_beds INTEGER DEFAULT 0,
            doctors INTEGER DEFAULT 0,
            medicines TEXT DEFAULT 'Available',
            phone TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_groups (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            blood_group TEXT NOT NULL UNIQUE,
            units INTEGER DEFAULT 0
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            requested_units INTEGER NOT NULL,
            phone TEXT NOT NULL,
            location TEXT NOT NULL,
            message TEXT,
            status TEXT DEFAULT 'Pending'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS medicines (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            category TEXT NOT NULL,
            availability TEXT DEFAULT 'Available'
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            specialization TEXT NOT NULL,
            hospital TEXT NOT NULL,
            location TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sos_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            message TEXT DEFAULT 'Emergency assistance requested',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            status TEXT DEFAULT 'Received by Tech4Life'
        )
    """)

    # Hospital table migration
    columns = [row["name"] for row in cursor.execute("PRAGMA table_info(hospitals)").fetchall()]

    if "total_beds" not in columns:
        cursor.execute(
            "ALTER TABLE hospitals ADD COLUMN total_beds INTEGER DEFAULT 0"
        )

    if "available_beds" not in columns:
        cursor.execute(
            "ALTER TABLE hospitals ADD COLUMN available_beds INTEGER DEFAULT 0"
        )

    cursor.execute("""
        UPDATE hospitals
        SET total_beds = beds,
            available_beds = beds
        WHERE total_beds = 0
        AND available_beds = 0
        AND beds > 0
    """)

    # Seed hospitals
    hospital_count = cursor.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]

    if hospital_count == 0:
        hospitals = [
            (
                "Max Super Speciality Hospital",
                "Rajpur Road, Dehradun",
                12,
                12,
                12,
                18,
                "Available",
                "+91 9876543210"
            ),
            (
                "Shri Mahant Indiresh Hospital",
                "Patel Nagar, Dehradun",
                8,
                8,
                6,
                14,
                "Available",
                "+91 9876543211"
            ),
            (
                "Doon Hospital",
                "Haridwar Road, Dehradun",
                5,
                5,
                2,
                10,
                "Limited",
                "+91 9876543212"
            ),
            (
                "Prem Nagar Community Hospital",
                "Prem Nagar, Dehradun",
                7,
                7,
                5,
                9,
                "Available",
                "+91 9876543213"
            ),
            (
                "Selaqui Healthcare Centre",
                "Selaqui, Dehradun",
                6,
                6,
                4,
                8,
                "Available",
                "+91 9876543214"
            ),
            (
                "Clement Town Hospital",
                "Clement Town, Dehradun",
                9,
                9,
                5,
                11,
                "Limited",
                "+91 9876543215"
            )
        ]

        cursor.executemany("""
            INSERT INTO hospitals
            (name, location, beds, total_beds, available_beds, doctors, medicines, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, hospitals)

    # Seed blood groups
    blood_count = cursor.execute(
        "SELECT COUNT(*) FROM blood_groups"
    ).fetchone()[0]

    if blood_count == 0:
        blood_groups = [
            ("A+", 12),
            ("A-", 5),
            ("B+", 18),
            ("B-", 7),
            ("O+", 25),
            ("O-", 8),
            ("AB+", 10),
            ("AB-", 3)
        ]

        cursor.executemany("""
            INSERT INTO blood_groups (blood_group, units)
            VALUES (?, ?)
        """, blood_groups)

    # Seed medicines
    medicine_count = cursor.execute(
        "SELECT COUNT(*) FROM medicines"
    ).fetchone()[0]

    if medicine_count == 0:
        medicines = [
            ("Paracetamol", "Pain Relief", "Available"),
            ("Amoxicillin", "Antibiotic", "Available"),
            ("Cetirizine", "Allergy Medicine", "Available"),
            ("Omeprazole", "Acidity Medicine", "Limited"),
            ("ORS", "Hydration", "Available"),
            ("Azithromycin", "Antibiotic", "Limited")
        ]

        cursor.executemany("""
            INSERT INTO medicines (name, category, availability)
            VALUES (?, ?, ?)
        """, medicines)

    # Seed doctors
    doctor_count = cursor.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    if doctor_count == 0:
        doctors = [
            (
                "Dr. Rahul Sharma",
                "General Physician",
                "Max Super Speciality Hospital",
                "Rajpur Road, Dehradun"
            ),
            (
                "Dr. Neha Verma",
                "Cardiologist",
                "Shri Mahant Indiresh Hospital",
                "Patel Nagar, Dehradun"
            ),
            (
                "Dr. Amit Singh",
                "Orthopedic",
                "Doon Hospital",
                "Haridwar Road, Dehradun"
            ),
            (
                "Dr. Priya Rawat",
                "Gynecologist",
                "Prem Nagar Community Hospital",
                "Prem Nagar, Dehradun"
            ),
            (
                "Dr. Ankit Negi",
                "Pediatrician",
                "Selaqui Healthcare Centre",
                "Selaqui, Dehradun"
            ),
            (
                "Dr. Pooja Joshi",
                "Dermatologist",
                "Clement Town Hospital",
                "Clement Town, Dehradun"
            )
        ]

        cursor.executemany("""
            INSERT INTO doctors
            (name, specialization, hospital, location)
            VALUES (?, ?, ?, ?)
        """, doctors)

    conn.commit()
    conn.close()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/blood-bank")
def blood_bank():
    conn = get_db_connection()
    blood_groups = conn.execute(
        "SELECT * FROM blood_groups ORDER BY blood_group"
    ).fetchall()
    conn.close()

    return render_template(
        "blood_bank.html",
        blood_groups=blood_groups
    )


@app.route("/hospitals")
def hospitals():
    search = request.args.get("search", "").strip()

    conn = get_db_connection()

    if search:
        hospitals = conn.execute("""
            SELECT * FROM hospitals
            WHERE name LIKE ?
            OR location LIKE ?
            ORDER BY id DESC
        """, (
            f"%{search}%",
            f"%{search}%"
        )).fetchall()
    else:
        hospitals = conn.execute("""
            SELECT * FROM hospitals
            ORDER BY id DESC
        """).fetchall()

    conn.close()

    return render_template(
        "hospitals.html",
        hospitals=hospitals,
        search=search
    )


@app.route("/hospital/<int:hospital_id>")
def hospital_details(hospital_id):
    conn = get_db_connection()

    hospital = conn.execute("""
        SELECT * FROM hospitals
        WHERE id = ?
    """, (hospital_id,)).fetchone()

    conn.close()

    if hospital is None:
        return redirect("/hospitals")

    return render_template(
        "hospital_details.html",
        hospital=hospital
    )


@app.route("/beds")
def beds():
    conn = get_db_connection()

    hospitals = conn.execute("""
        SELECT * FROM hospitals
        ORDER BY available_beds DESC
    """).fetchall()

    conn.close()

    return render_template(
        "beds.html",
        hospitals=hospitals
    )


@app.route("/doctors")
def doctors():
    search = request.args.get("search", "").strip()
    specialization = request.args.get("specialization", "").strip()

    conn = get_db_connection()

    specializations = conn.execute("""
        SELECT DISTINCT specialization
        FROM doctors
        ORDER BY specialization
    """).fetchall()

    query = "SELECT * FROM doctors WHERE 1=1"
    params = []

    if search:
        query += """
            AND (
                name LIKE ?
                OR hospital LIKE ?
                OR location LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value,
            search_value
        ])

    if specialization:
        query += " AND specialization = ?"
        params.append(specialization)

    query += " ORDER BY id DESC"

    doctors = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return render_template(
        "doctors.html",
        doctors=doctors,
        search=search,
        specialization=specialization,
        specializations=specializations
    )


@app.route("/medicines")
def medicines():
    search = request.args.get("search", "").strip()
    category = request.args.get("category", "").strip()

    conn = get_db_connection()

    categories = conn.execute("""
        SELECT DISTINCT category
        FROM medicines
        ORDER BY category
    """).fetchall()

    query = "SELECT * FROM medicines WHERE 1=1"
    params = []

    if search:
        query += """
            AND (
                name LIKE ?
                OR category LIKE ?
            )
        """

        search_value = f"%{search}%"

        params.extend([
            search_value,
            search_value
        ])

    if category:
        query += " AND category = ?"
        params.append(category)

    query += " ORDER BY id DESC"

    medicines = conn.execute(
        query,
        params
    ).fetchall()

    conn.close()

    return render_template(
        "medicines.html",
        medicines=medicines,
        search=search,
        category=category,
        categories=categories
    )


@app.route("/nearby")
def nearby():
    return render_template("nearby.html")


@app.route("/hospital-tracking")
def hospital_tracking():
    return render_template("hospital_tracking.html")


@app.route("/api/sos", methods=["POST"])
def create_sos_alert():
    """Store an SOS request and return a receipt.

    This records the request in Tech4Life; it does not automatically notify
    hospitals. A verified hospital notification integration is required.
    """
    data = request.get_json(silent=True) or {}
    try:
        latitude = float(data.get("latitude"))
        longitude = float(data.get("longitude"))
    except (TypeError, ValueError):
        return jsonify({"ok": False, "message": "Valid location coordinates are required."}), 400

    if not (-90 <= latitude <= 90 and -180 <= longitude <= 180):
        return jsonify({"ok": False, "message": "Location coordinates are out of range."}), 400

    conn = get_db_connection()
    cursor = conn.execute(
        "INSERT INTO sos_alerts (latitude, longitude, message) VALUES (?, ?, ?)",
        (latitude, longitude, "Emergency assistance requested")
    )
    alert_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        "ok": True,
        "alert_id": alert_id,
        "message": "SOS request has been recorded in Tech4Life."
    }), 201


@app.route("/request-blood", methods=["GET", "POST"])
def request_blood():
    if request.method == "POST":

        patient_name = request.form.get("patient_name", "").strip()
        blood_group = request.form.get("blood_group", "").strip()
        units_text = request.form.get("units", "").strip()
        phone = request.form.get("phone", "").strip()
        location = request.form.get("location", "").strip()
        message = request.form.get("message", "").strip()

        selected_group = blood_group

        # Basic validation
        if not patient_name or not blood_group or not units_text or not phone or not location:
            return render_template(
                "request_blood.html",
                error="Please fill all required fields.",
                selected_group=selected_group
            )

        try:
            units = int(units_text)
        except ValueError:
            return render_template(
                "request_blood.html",
                error="Please enter a valid number of blood units.",
                selected_group=selected_group
            )

        if units < 1:
            return render_template(
                "request_blood.html",
                error="Blood units must be at least 1.",
                selected_group=selected_group
            )

        conn = get_db_connection()

        blood = conn.execute("""
            SELECT * FROM blood_groups
            WHERE blood_group = ?
        """, (blood_group,)).fetchone()

        if blood is None:
            conn.close()

            return render_template(
                "request_blood.html",
                error="Invalid blood group selected.",
                selected_group=selected_group
            )

        if units > blood["units"]:
            available_units = blood["units"]
            conn.close()

            return render_template(
                "request_blood.html",
                error=f"Only {available_units} units of {blood_group} blood are currently available.",
                selected_group=selected_group
            )

        conn.execute("""
            INSERT INTO blood_requests
            (patient_name, blood_group, requested_units, phone, location, message, status)
            VALUES (?, ?, ?, ?, ?, ?, 'Pending')
        """, (
            patient_name,
            blood_group,
            units,
            phone,
            location,
            message
        ))

        conn.commit()
        conn.close()

        return redirect("/request-success")

    return render_template(
        "request_blood.html",
        selected_group=""
    )


@app.route("/request-success")
def request_success():
    return render_template("request_success.html")


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "").strip()

        if username == "admin" and password == "admin123":
            session["admin_logged_in"] = True
            return redirect("/admin")

        return render_template(
            "admin_login.html",
            error="Invalid username or password."
        )

    return render_template("admin_login.html")


@app.route("/admin")
def admin():

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    total_hospitals = conn.execute(
        "SELECT COUNT(*) FROM hospitals"
    ).fetchone()[0]

    total_doctors = conn.execute(
        "SELECT COUNT(*) FROM doctors"
    ).fetchone()[0]

    total_medicines = conn.execute(
        "SELECT COUNT(*) FROM medicines"
    ).fetchone()[0]

    total_blood_units = conn.execute(
        "SELECT COALESCE(SUM(units), 0) FROM blood_groups"
    ).fetchone()[0]

    total_beds = conn.execute(
        "SELECT COALESCE(SUM(total_beds), 0) FROM hospitals"
    ).fetchone()[0]

    available_beds = conn.execute(
        "SELECT COALESCE(SUM(available_beds), 0) FROM hospitals"
    ).fetchone()[0]

    pending_requests = conn.execute("""
        SELECT COUNT(*) FROM blood_requests
        WHERE status = 'Pending'
    """).fetchone()[0]

    approved_requests = conn.execute("""
        SELECT COUNT(*) FROM blood_requests
        WHERE status = 'Approved'
    """).fetchone()[0]

    rejected_requests = conn.execute("""
        SELECT COUNT(*) FROM blood_requests
        WHERE status = 'Rejected'
    """).fetchone()[0]

    completed_requests = conn.execute("""
        SELECT COUNT(*) FROM blood_requests
        WHERE status = 'Completed'
    """).fetchone()[0]

    hospitals = conn.execute("""
        SELECT * FROM hospitals
        ORDER BY id DESC
    """).fetchall()

    blood_groups = conn.execute("""
        SELECT * FROM blood_groups
        ORDER BY blood_group
    """).fetchall()

    blood_requests = conn.execute("""
        SELECT * FROM blood_requests
        ORDER BY id DESC
    """).fetchall()

    medicines = conn.execute("""
        SELECT * FROM medicines
        ORDER BY id DESC
    """).fetchall()

    doctors = conn.execute("""
        SELECT * FROM doctors
        ORDER BY id DESC
    """).fetchall()

    medicine_available = conn.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE availability = 'Available'
    """).fetchone()[0]

    medicine_limited = conn.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE availability = 'Limited'
    """).fetchone()[0]

    medicine_unavailable = conn.execute("""
        SELECT COUNT(*) FROM medicines
        WHERE availability = 'Unavailable'
    """).fetchone()[0]

    conn.close()

    return render_template(
        "admin.html",
        total_hospitals=total_hospitals,
        total_doctors=total_doctors,
        total_medicines=total_medicines,
        total_blood_units=total_blood_units,
        total_beds=total_beds,
        available_beds=available_beds,
        pending_requests=pending_requests,
        approved_requests=approved_requests,
        rejected_requests=rejected_requests,
        completed_requests=completed_requests,
        blood_chart=blood_groups,
        medicine_available=medicine_available,
        medicine_limited=medicine_limited,
        medicine_unavailable=medicine_unavailable,
        hospitals=hospitals,
        blood_groups=blood_groups,
        blood_requests=blood_requests,
        medicines=medicines,
        doctors=doctors
    )


@app.route("/admin/hospital/add", methods=["GET", "POST"])
def add_hospital():

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        total_beds_text = request.form.get("total_beds", "0").strip()
        available_beds_text = request.form.get("available_beds", "0").strip()
        doctors_text = request.form.get("doctors", "0").strip()
        medicines = request.form.get("medicines", "Available").strip()
        phone = request.form.get("phone", "").strip()

        try:
            total_beds = int(total_beds_text)
            available_beds = int(available_beds_text)
            doctors = int(doctors_text)
        except ValueError:
            return render_template(
                "hospital_form.html",
                error="Beds and doctors must be valid numbers.",
                hospital=None
            )

        if not name or not location or not phone:
            return render_template(
                "hospital_form.html",
                error="Please fill all required fields.",
                hospital=None
            )

        if total_beds < 0 or available_beds < 0 or doctors < 0:
            return render_template(
                "hospital_form.html",
                error="Values cannot be negative.",
                hospital=None
            )

        if available_beds > total_beds:
            return render_template(
                "hospital_form.html",
                error="Available beds cannot be greater than total beds.",
                hospital=None
            )

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO hospitals
            (name, location, beds, total_beds, available_beds, doctors, medicines, phone)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            name,
            location,
            total_beds,
            total_beds,
            available_beds,
            doctors,
            medicines,
            phone
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template(
        "hospital_form.html",
        hospital=None
    )


@app.route("/admin/hospital/edit/<int:hospital_id>", methods=["GET", "POST"])
def edit_hospital(hospital_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    hospital = conn.execute("""
        SELECT * FROM hospitals
        WHERE id = ?
    """, (hospital_id,)).fetchone()

    if hospital is None:
        conn.close()
        return redirect("/admin")

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        location = request.form.get("location", "").strip()
        total_beds_text = request.form.get("total_beds", "0").strip()
        available_beds_text = request.form.get("available_beds", "0").strip()
        doctors_text = request.form.get("doctors", "0").strip()
        medicines = request.form.get("medicines", "Available").strip()
        phone = request.form.get("phone", "").strip()

        try:
            total_beds = int(total_beds_text)
            available_beds = int(available_beds_text)
            doctors = int(doctors_text)
        except ValueError:
            conn.close()

            return render_template(
                "hospital_form.html",
                error="Beds and doctors must be valid numbers.",
                hospital=hospital
            )

        if not name or not location or not phone:
            conn.close()

            return render_template(
                "hospital_form.html",
                error="Please fill all required fields.",
                hospital=hospital
            )

        if total_beds < 0 or available_beds < 0 or doctors < 0:
            conn.close()

            return render_template(
                "hospital_form.html",
                error="Values cannot be negative.",
                hospital=hospital
            )

        if available_beds > total_beds:
            conn.close()

            return render_template(
                "hospital_form.html",
                error="Available beds cannot be greater than total beds.",
                hospital=hospital
            )

        conn.execute("""
            UPDATE hospitals
            SET name = ?,
                location = ?,
                beds = ?,
                total_beds = ?,
                available_beds = ?,
                doctors = ?,
                medicines = ?,
                phone = ?
            WHERE id = ?
        """, (
            name,
            location,
            total_beds,
            total_beds,
            available_beds,
            doctors,
            medicines,
            phone,
            hospital_id
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    conn.close()

    return render_template(
        "hospital_form.html",
        hospital=hospital
    )


@app.route("/admin/hospital/delete/<int:hospital_id>", methods=["POST"])
def delete_hospital(hospital_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM hospitals
        WHERE id = ?
    """, (hospital_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin/blood/add", methods=["GET", "POST"])
def add_blood():

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    error = None

    if request.method == "POST":

        blood_group = request.form.get("blood_group", "").strip()
        units_text = request.form.get("units", "").strip()

        try:
            units = int(units_text)
        except ValueError:
            return render_template(
                "blood_form.html",
                error="Units must be a valid number.",
                blood=None
            )

        if units < 0:
            return render_template(
                "blood_form.html",
                error="Units cannot be negative.",
                blood=None
            )

        conn = get_db_connection()

        existing = conn.execute("""
            SELECT * FROM blood_groups
            WHERE blood_group = ?
        """, (blood_group,)).fetchone()

        if existing:
            conn.close()

            return render_template(
                "blood_form.html",
                error="This blood group already exists.",
                blood=None
            )

        conn.execute("""
            INSERT INTO blood_groups
            (blood_group, units)
            VALUES (?, ?)
        """, (
            blood_group,
            units
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template(
        "blood_form.html",
        error=error,
        blood=None
    )


@app.route("/admin/blood/edit/<int:blood_id>", methods=["GET", "POST"])
def edit_blood(blood_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    blood = conn.execute("""
        SELECT * FROM blood_groups
        WHERE id = ?
    """, (blood_id,)).fetchone()

    if blood is None:
        conn.close()
        return redirect("/admin")

    if request.method == "POST":

        blood_group = request.form.get("blood_group", "").strip()
        units_text = request.form.get("units", "").strip()

        try:
            units = int(units_text)
        except ValueError:
            conn.close()

            return render_template(
                "blood_form.html",
                error="Units must be a valid number.",
                blood=blood
            )

        if units < 0:
            conn.close()

            return render_template(
                "blood_form.html",
                error="Units cannot be negative.",
                blood=blood
            )

        duplicate = conn.execute("""
            SELECT id FROM blood_groups
            WHERE blood_group = ?
            AND id != ?
        """, (
            blood_group,
            blood_id
        )).fetchone()

        if duplicate:
            conn.close()

            return render_template(
                "blood_form.html",
                error="This blood group already exists.",
                blood=blood
            )

        conn.execute("""
            UPDATE blood_groups
            SET blood_group = ?,
                units = ?
            WHERE id = ?
        """, (
            blood_group,
            units,
            blood_id
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    conn.close()

    return render_template(
        "blood_form.html",
        error=None,
        blood=blood
    )


@app.route("/admin/blood/delete/<int:blood_id>", methods=["POST"])
def delete_blood(blood_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM blood_groups
        WHERE id = ?
    """, (blood_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin/request/<int:request_id>/approve", methods=["POST"])
def approve_request(request_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    blood_request = conn.execute("""
        SELECT * FROM blood_requests
        WHERE id = ?
    """, (request_id,)).fetchone()

    if blood_request is None:
        conn.close()
        return redirect("/admin")

    if blood_request["status"] != "Pending":
        conn.close()
        return redirect("/admin")

    blood = conn.execute("""
        SELECT * FROM blood_groups
        WHERE blood_group = ?
    """, (blood_request["blood_group"],)).fetchone()

    if blood is None:
        conn.close()
        return redirect("/admin")

    requested_units = blood_request["requested_units"]

    if requested_units > blood["units"]:
        conn.close()
        return redirect("/admin")

    conn.execute("""
        UPDATE blood_groups
        SET units = units - ?
        WHERE blood_group = ?
    """, (
        requested_units,
        blood_request["blood_group"]
    ))

    conn.execute("""
        UPDATE blood_requests
        SET status = 'Approved'
        WHERE id = ?
    """, (request_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin/request/<int:request_id>/reject", methods=["POST"])
def reject_request(request_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    conn.execute("""
        UPDATE blood_requests
        SET status = 'Rejected'
        WHERE id = ?
        AND status = 'Pending'
    """, (request_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin/request/<int:request_id>/complete", methods=["POST"])
def complete_request(request_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    conn.execute("""
        UPDATE blood_requests
        SET status = 'Completed'
        WHERE id = ?
        AND status = 'Approved'
    """, (request_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin/medicine/add", methods=["GET", "POST"])
def add_medicine():

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        availability = request.form.get("availability", "Available").strip()

        if not name or not category:
            return render_template(
                "medicine_form.html",
                error="Please fill all required fields.",
                medicine=None
            )

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO medicines
            (name, category, availability)
            VALUES (?, ?, ?)
        """, (
            name,
            category,
            availability
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template(
        "medicine_form.html",
        medicine=None
    )


@app.route("/admin/medicine/edit/<int:medicine_id>", methods=["GET", "POST"])
def edit_medicine(medicine_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    medicine = conn.execute("""
        SELECT * FROM medicines
        WHERE id = ?
    """, (medicine_id,)).fetchone()

    if medicine is None:
        conn.close()
        return redirect("/admin")

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        category = request.form.get("category", "").strip()
        availability = request.form.get("availability", "Available").strip()

        if not name or not category:
            conn.close()

            return render_template(
                "medicine_form.html",
                error="Please fill all required fields.",
                medicine=medicine
            )

        conn.execute("""
            UPDATE medicines
            SET name = ?,
                category = ?,
                availability = ?
            WHERE id = ?
        """, (
            name,
            category,
            availability,
            medicine_id
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    conn.close()

    return render_template(
        "medicine_form.html",
        medicine=medicine
    )


@app.route("/admin/medicine/delete/<int:medicine_id>", methods=["POST"])
def delete_medicine(medicine_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM medicines
        WHERE id = ?
    """, (medicine_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin/doctor/add", methods=["GET", "POST"])
def add_doctor():

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        specialization = request.form.get("specialization", "").strip()
        hospital = request.form.get("hospital", "").strip()
        location = request.form.get("location", "").strip()

        if not name or not specialization or not hospital or not location:
            return render_template(
                "doctor_form.html",
                error="Please fill all required fields.",
                doctor=None
            )

        conn = get_db_connection()

        conn.execute("""
            INSERT INTO doctors
            (name, specialization, hospital, location)
            VALUES (?, ?, ?, ?)
        """, (
            name,
            specialization,
            hospital,
            location
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    return render_template(
        "doctor_form.html",
        doctor=None
    )


@app.route("/admin/doctor/edit/<int:doctor_id>", methods=["GET", "POST"])
def edit_doctor(doctor_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    doctor = conn.execute("""
        SELECT * FROM doctors
        WHERE id = ?
    """, (doctor_id,)).fetchone()

    if doctor is None:
        conn.close()
        return redirect("/admin")

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        specialization = request.form.get("specialization", "").strip()
        hospital = request.form.get("hospital", "").strip()
        location = request.form.get("location", "").strip()

        if not name or not specialization or not hospital or not location:
            conn.close()

            return render_template(
                "doctor_form.html",
                error="Please fill all required fields.",
                doctor=doctor
            )

        conn.execute("""
            UPDATE doctors
            SET name = ?,
                specialization = ?,
                hospital = ?,
                location = ?
            WHERE id = ?
        """, (
            name,
            specialization,
            hospital,
            location,
            doctor_id
        ))

        conn.commit()
        conn.close()

        return redirect("/admin")

    conn.close()

    return render_template(
        "doctor_form.html",
        doctor=doctor
    )


@app.route("/admin/doctor/delete/<int:doctor_id>", methods=["POST"])
def delete_doctor(doctor_id):

    if not session.get("admin_logged_in"):
        return redirect("/admin/login")

    conn = get_db_connection()

    conn.execute("""
        DELETE FROM doctors
        WHERE id = ?
    """, (doctor_id,))

    conn.commit()
    conn.close()

    return redirect("/admin")


@app.route("/admin/sos")
def admin_sos():
    if not session.get("admin_logged_in"):
        return redirect("/admin/login")
    conn = get_db_connection()
    alerts = conn.execute("SELECT * FROM sos_alerts ORDER BY id DESC LIMIT 100").fetchall()
    conn.close()
    return render_template("admin_sos.html", alerts=alerts)


@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect("/admin/login")


@app.errorhandler(404)
def page_not_found(error):
    return """
    <div style="
        font-family: Arial;
        text-align: center;
        padding: 80px 20px;
    ">
        <h1 style="color:#0b5ed7;">404 - Page Not Found</h1>
        <p>The page you are looking for does not exist.</p>
        <a href="/" style="
            display:inline-block;
            margin-top:20px;
            padding:12px 20px;
            background:#0b5ed7;
            color:white;
            text-decoration:none;
            border-radius:8px;
        ">
            Go to Tech4Life Home
        </a>
    </div>
    """, 404


@app.errorhandler(500)
def server_error(error):
    return """
    <div style="
        font-family: Arial;
        text-align: center;
        padding: 80px 20px;
    ">
        <h1 style="color:#dc3545;">500 - Server Error</h1>
        <p>Something went wrong on the server.</p>
        <a href="/" style="
            display:inline-block;
            margin-top:20px;
            padding:12px 20px;
            background:#0b5ed7;
            color:white;
            text-decoration:none;
            border-radius:8px;
        ">
            Go to Tech4Life Home
        </a>
    </div>
    """, 500


if __name__ == "__main__":
    create_database()
    app.run(debug=True)