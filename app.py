from flask import Flask, render_template, request, jsonify, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, re

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "college-chatbot-secret-key")
DB = os.path.join(os.path.dirname(__file__), "college.db")

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT DEFAULT 'student'
    )""")

    cur.execute("""CREATE TABLE IF NOT EXISTS college_info(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        category TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL
    )""")

    count = cur.execute("SELECT COUNT(*) FROM college_info").fetchone()[0]
    if count == 0:
        data = [
            ("courses", "What courses are available?",
             "Our college offers B.E./B.Tech, M.E./M.Tech and other programs. Please contact the admission office for the current course list."),
            ("courses", "What is the eligibility for Computer Science?",
             "For B.E./B.Tech Computer Science, eligibility generally includes completion of higher secondary education with the required subjects and marks. Check the current admission notification for exact requirements."),
            ("admission", "What is the admission process?",
             "The admission process generally includes application, document verification, eligibility verification, fee payment and confirmation of admission."),
            ("admission", "What documents are required?",
             "Common documents include 10th and 12th mark sheets, transfer certificate, community certificate where applicable, Aadhaar/ID proof, passport-size photographs and other documents requested by the college."),
            ("fees", "What is the college fee?",
             "Fees vary by course, quota and academic year. Please check the latest fee circular or contact the accounts/admission office for the exact amount."),
            ("fees", "What is the hostel fee?",
             "Hostel fees depend on room type and academic year. Contact the hostel office for the latest fee structure."),
            ("department", "Tell me about the Computer Science department.",
             "The Computer Science department focuses on programming, databases, artificial intelligence, cloud computing, cybersecurity and software development."),
            ("academic_calendar", "When are semester exams?",
             "Semester examination dates are published in the academic calendar. Update the college database with the latest examination schedule."),
            ("timetable", "Where can I find the class timetable?",
             "Class timetables are available from the department/college timetable section. The latest timetable should be updated in the college database."),
            ("announcements", "What are the latest announcements?",
             "Please check the latest college notices and announcements section. Administrators can update announcements in the college database."),
            ("library", "What are the library timings?",
             "Library timings can be updated here according to your college. Example: Monday-Friday 9:00 AM to 5:00 PM."),
            ("library", "What facilities are available in the library?",
             "The library can provide textbooks, reference books, journals, digital resources, reading areas and computer/internet facilities."),
            ("hostel", "What hostel facilities are available?",
             "Hostel facilities may include rooms, dining/mess, drinking water, study areas, security and internet facilities. Contact the hostel office for current details."),
            ("canteen", "What are the canteen timings?",
             "Canteen timings can be updated according to your college schedule. Example: 8:00 AM to 5:00 PM on working days."),
            ("transport", "Does the college have bus transport?",
             "Yes, college transport information such as routes, stops and timings can be maintained in the database."),
            ("transport", "What are the bus routes?",
             "Please update the transport section with your college's actual routes and pickup timings."),
            ("navigation", "Where is the Computer Science department?",
             "The Computer Science department location can be updated here, for example: Main Block, First Floor."),
            ("contact", "How can I contact the admission office?",
             "Update this answer with your college admission office phone number, email and working hours."),
            ("contact", "How can I contact the college office?",
             "Update this answer with the main office phone number, email and working hours.")
        ]
        cur.executemany("INSERT INTO college_info(category,question,answer) VALUES(?,?,?)", data)

    conn.commit()
    conn.close()

def normalize(text):
    return re.sub(r"[^a-z0-9 ]", " ", text.lower()).split()

def chatbot_answer(message):
    words = set(normalize(message))
    conn = get_db()
    rows = conn.execute("SELECT * FROM college_info").fetchall()
    conn.close()

    best = None
    best_score = 0

    for row in rows:
        qwords = set(normalize(row["question"]))
        score = len(words & qwords)
        if row["category"] in message.lower():
            score += 2
        if score > best_score:
            best_score = score
            best = row

    if best and best_score > 0:
        return best["answer"]

    # Simple category fallback
    categories = {
        "course": "courses", "department": "department", "admission": "admission",
        "fee": "fees", "fees": "fees", "hostel": "hostel", "library": "library",
        "canteen": "canteen", "bus": "transport", "transport": "transport",
        "timetable": "timetable", "exam": "academic_calendar",
        "calendar": "academic_calendar", "announcement": "announcements",
        "notice": "announcements", "contact": "contact", "office": "contact"
    }
    for key, category in categories.items():
        if key in message.lower():
            conn = get_db()
            row = conn.execute(
                "SELECT answer FROM college_info WHERE category=? LIMIT 1", (category,)
            ).fetchone()
            conn.close()
            if row:
                return row["answer"]

    return ("Sorry, I couldn't find that information in the college database. "
            "Please try asking about courses, admission, fees, departments, "
            "calendar, timetable, library, hostel, canteen, transport or contacts.")

@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    return render_template("index.html", name=session.get("name"), role=session.get("role"))

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"].strip()
        email = request.form["email"].strip().lower()
        password = request.form["password"]
        role = request.form.get("role", "student")

        if not name or not email or not password:
            flash("All fields are required.")
            return redirect(url_for("register"))

        conn = get_db()
        try:
            conn.execute(
                "INSERT INTO users(name,email,password,role) VALUES(?,?,?,?)",
                (name, email, generate_password_hash(password), role)
            )
            conn.commit()
            flash("Registration successful. Please login.")
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            flash("Email already registered.")
            return redirect(url_for("register"))
        finally:
            conn.close()

    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"].strip().lower()
        password = request.form["password"]

        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone()
        conn.close()

        if user and check_password_hash(user["password"], password):
            session["user_id"] = user["id"]
            session["name"] = user["name"]
            session["role"] = user["role"]
            return redirect(url_for("index"))

        flash("Invalid email or password.")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/chat", methods=["POST"])
def chat():
    if "user_id" not in session:
        return jsonify({"answer": "Please login first."}), 401

    data = request.get_json()
    message = (data.get("message") or "").strip()

    if not message:
        return jsonify({"answer": "Please enter a question."})

    return jsonify({"answer": chatbot_answer(message)})

@app.route("/api/info/<category>")
def info(category):
    conn = get_db()
    rows = conn.execute(
        "SELECT question, answer FROM college_info WHERE category=?",
        (category,)
    ).fetchall()
    conn.close()
    return jsonify([dict(row) for row in rows])

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
