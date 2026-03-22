from flask import Flask, render_template, request
import sqlite3
import os

app = Flask(__name__)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cars.db')


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS cars (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            engine TEXT NOT NULL,
            horsepower INTEGER NOT NULL,
            top_speed INTEGER NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS services (
            service_id INTEGER PRIMARY KEY AUTOINCREMENT,
            service_name TEXT NOT NULL,
            price INTEGER NOT NULL
        )
    """)

    c.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            brand TEXT NOT NULL,
            model TEXT NOT NULL,
            service TEXT NOT NULL
        )
    """)

    c.execute("SELECT COUNT(*) FROM cars")
    if c.fetchone()[0] == 0:
        cars = [
            ("Toyota",      "AE86",           "1.6L 4A-GE",       128, 180),
            ("Nissan",      "GTR R34",         "2.6L RB26DETT",    276, 250),
            ("Mazda",       "RX-7",            "1.3L Rotary 13B",  276, 250),
            ("Subaru",      "Impreza WRX STI", "2.0L EJ20T",       280, 240),
            ("Mitsubishi",  "Lancer Evo IX",   "2.0L 4G63T",       286, 245),
            ("Honda",       "Civic Type R",    "1.6L B16B",        185, 230),
            ("Toyota",      "Supra MK4",       "3.0L 2JZ-GTE",     320, 270),
            ("Nissan",      "Silvia S15",      "2.0L SR20DET",     250, 230),
        ]
        c.executemany(
            "INSERT INTO cars (brand, model, engine, horsepower, top_speed) VALUES (?,?,?,?,?)",
            cars
        )

    c.execute("SELECT COUNT(*) FROM services")
    if c.fetchone()[0] == 0:
        services = [
            ("Stage 1 ECU Tune",           800),
            ("Turbo Upgrade",             2500),
            ("Suspension Setup",          1200),
            ("Performance Exhaust",        950),
            ("Cold Air Intake",            450),
            ("Brake Upgrade Kit",         1100),
            ("Limited Slip Differential", 1800),
            ("Coilover Kit",              1600),
        ]
        c.executemany(
            "INSERT INTO services (service_name, price) VALUES (?,?)",
            services
        )

    conn.commit()
    conn.close()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


@app.route("/search", methods=["POST"])
def search():
    brand = request.form.get("brand", "").strip()
    model = request.form.get("model", "").strip()

    conn = get_db()
    car = conn.execute(
        "SELECT * FROM cars WHERE LOWER(brand)=LOWER(?) AND LOWER(model)=LOWER(?)",
        (brand, model)
    ).fetchone()
    services = conn.execute("SELECT * FROM services").fetchall()
    conn.close()

    return render_template("result.html", car=car, services=services,
                           searched_brand=brand, searched_model=model)


@app.route("/booking", methods=["GET"])
def booking():
    brand   = request.args.get("brand", "")
    model   = request.args.get("model", "")
    service = request.args.get("service", "")
    return render_template("booking.html", brand=brand, model=model, service=service)


@app.route("/submit_booking", methods=["POST"])
def submit_booking():
    name    = request.form.get("name", "").strip()
    email   = request.form.get("email", "").strip()
    brand   = request.form.get("brand", "").strip()
    model   = request.form.get("model", "").strip()
    service = request.form.get("service", "").strip()

    conn = get_db()
    conn.execute(
        "INSERT INTO bookings (name, email, brand, model, service) VALUES (?,?,?,?,?)",
        (name, email, brand, model, service)
    )
    conn.commit()
    conn.close()

    return render_template("booking.html", confirmed=True,
                           name=name, brand=brand, model=model, service=service)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)


init_db()
