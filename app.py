from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
import os
from google import genai
from utils.gemini_helper import analyze_image
from database import init_db, save_report

# Load environment variables
load_dotenv()

app = Flask(__name__)
init_db()

# Gemini Client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/report")
def report():
    return render_template("report.html")

import sqlite3

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    cursor.execute("SELECT * FROM reports ORDER BY id DESC")
    reports = cursor.fetchall()

    cursor.execute("SELECT COUNT(*) FROM reports")
    total_reports = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE severity='High'")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE severity='Medium'")
    medium = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE severity='Low'")
    low = cursor.fetchone()[0]

    conn.close()

    return render_template(
        "dashboard.html",
        reports=reports,
        total_reports=total_reports,
        high=high,
        medium=medium,
        low=low
    )

@app.route("/login")
def login():
    return "<h1>Login Coming Soon</h1>"

@app.route("/analyze", methods=["POST"])
def analyze():

    image = request.files["image"]

    save_path = os.path.join("uploads", image.filename)

    image.save(save_path)

    result = analyze_image(save_path)

    save_report(result, save_path)

    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)