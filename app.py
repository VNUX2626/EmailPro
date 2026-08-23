from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sqlite3, os, csv, re
from datetime import datetime

app = Flask(__name__)
app.secret_key = "emailpro-demo-secret"
BASE = os.path.dirname(os.path.abspath(__file__))
DB = os.path.join(BASE, "emailpro.db")
UPLOADS = os.path.join(BASE, "uploads")
os.makedirs(UPLOADS, exist_ok=True)

def db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = db()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS emails(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        name TEXT DEFAULT '',
        category TEXT DEFAULT 'Unclassified',
        status TEXT DEFAULT 'Pending',
        created_at TEXT NOT NULL
    );
    CREATE TABLE IF NOT EXISTS campaigns(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        subject TEXT NOT NULL,
        audience TEXT DEFAULT 'All',
        content TEXT DEFAULT '',
        sent INTEGER DEFAULT 0,
        failed INTEGER DEFAULT 0,
        created_at TEXT NOT NULL
    );
    """)
    conn.commit()
    conn.close()
    init_db()
def classify(email):
    e = email.lower()
    if any(x in e for x in ["bounce", "noreply", "no-reply"]):
        return "Invalid/Unwanted"
    if re.search(r"@(gmail|outlook|yahoo|hotmail)\.", e):
        return "Personal"
    return "Business"

@app.route("/")
def index():
    conn = db()
    stats = {
        "emails": conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0],
        "business": conn.execute("SELECT COUNT(*) FROM emails WHERE category='Business'").fetchone()[0],
        "personal": conn.execute("SELECT COUNT(*) FROM emails WHERE category='Personal'").fetchone()[0],
        "campaigns": conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0],
        "sent": conn.execute("SELECT COALESCE(SUM(sent),0) FROM campaigns").fetchone()[0],
        "failed": conn.execute("SELECT COALESCE(SUM(failed),0) FROM campaigns").fetchone()[0]
    }
    campaigns = conn.execute("SELECT * FROM campaigns ORDER BY id DESC LIMIT 5").fetchall()
    conn.close()
    return render_template("index.html", stats=stats, campaigns=campaigns)

@app.route("/emails", methods=["GET", "POST"])
def emails():
    conn = db()
    if request.method == "POST":
        file = request.files.get("file")
        if not file or not file.filename:
            flash("Please choose a CSV file.")
            return redirect(url_for("emails"))
        path = os.path.join(UPLOADS, file.filename)
        file.save(path)
        added = 0
        with open(path, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                email = (row.get("email") or row.get("Email") or "").strip()
                name = (row.get("name") or row.get("Name") or "").strip()
                if email and "@" in email:
                    conn.execute(
                        "INSERT INTO emails(email,name,category,status,created_at) VALUES(?,?,?,?,?)",
                        (email, name, classify(email), "Ready", datetime.now().isoformat(timespec="seconds"))
                    )
                    added += 1
        conn.commit()
        flash(f"Imported {added} email(s).")
        return redirect(url_for("emails"))
    rows = conn.execute("SELECT * FROM emails ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("emails.html", emails=rows)

@app.route("/campaigns", methods=["GET", "POST"])
def campaigns():
    conn = db()
    if request.method == "POST":
        name = request.form.get("name","").strip()
        subject = request.form.get("subject","").strip()
        audience = request.form.get("audience","All")
        content = request.form.get("content","").strip()
        count = conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0]
        if not name or not subject:
            flash("Campaign name and subject are required.")
            return redirect(url_for("campaigns"))
        # Demo mode: no real emails are sent.
        sent = count if count else 0
        failed = 0
        conn.execute(
            "INSERT INTO campaigns(name,subject,audience,content,sent,failed,created_at) VALUES(?,?,?,?,?,?,?)",
            (name, subject, audience, content, sent, failed, datetime.now().isoformat(timespec="seconds"))
        )
        conn.commit()
        flash(f"Campaign created in demo mode. {sent} recipient(s) marked as ready.")
        return redirect(url_for("campaigns"))
    rows = conn.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("campaigns.html", campaigns=rows)

@app.route("/reports")
def reports():
    conn = db()
    rows = conn.execute("SELECT * FROM campaigns ORDER BY id DESC").fetchall()
    totals = conn.execute("SELECT COALESCE(SUM(sent),0), COALESCE(SUM(failed),0) FROM campaigns").fetchone()
    conn.close()
    return render_template("reports.html", campaigns=rows, total_sent=totals[0], total_failed=totals[1])

@app.route("/api/stats")
def api_stats():
    conn = db()
    result = {
        "emails": conn.execute("SELECT COUNT(*) FROM emails").fetchone()[0],
        "campaigns": conn.execute("SELECT COUNT(*) FROM campaigns").fetchone()[0],
        "sent": conn.execute("SELECT COALESCE(SUM(sent),0) FROM campaigns").fetchone()[0],
        "failed": conn.execute("SELECT COALESCE(SUM(failed),0) FROM campaigns").fetchone()[0]
    }
    conn.close()
    return jsonify(result)

@app.route("/settings")
def settings():
    return render_template("settings.html")

if __name__ == "__main__":
    init_db()
    app.run(debug=True)
