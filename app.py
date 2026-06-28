from flask import Flask, render_template, request, jsonify, send_from_directory
from dotenv import load_dotenv
import sqlite3
import os
import uuid

from utils.gemini_helper import analyze_image
from database import init_db, save_report

# ==============================
# Load Environment
# ==============================

load_dotenv()

app = Flask(__name__)

os.makedirs("uploads", exist_ok=True)

init_db()


# ==============================
# Routes
# ==============================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/report")
def report():
    return render_template("report.html")


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    return send_from_directory("uploads", filename)


# ==============================
# Dashboard
# ==============================

@app.route("/dashboard")
def dashboard():

    conn = sqlite3.connect("database.db")
    conn.row_factory = sqlite3.Row

    cursor = conn.cursor()

    # -----------------------------
    # Reports
    # -----------------------------
    cursor.execute("SELECT * FROM reports ORDER BY id DESC")
    reports = cursor.fetchall()

    # -----------------------------
    # Statistics
    # -----------------------------
    cursor.execute("SELECT COUNT(*) FROM reports")
    total_reports = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE severity='High'")
    high = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE severity='Medium'")
    medium = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reports WHERE severity='Low'")
    low = cursor.fetchone()[0]

    # -----------------------------
    # AI Insight 1
    # Most reported category
    # -----------------------------
    cursor.execute("""
        SELECT category, COUNT(*) AS total
        FROM reports
        GROUP BY category
        ORDER BY total DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    highest_category = row["category"] if row else "No Data"

    # -----------------------------
    # AI Insight 2
    # Hotspot location
    # -----------------------------
    cursor.execute("""
        SELECT location, COUNT(*) AS total
        FROM reports
        WHERE location != ''
        GROUP BY location
        ORDER BY total DESC
        LIMIT 1
    """)

    row = cursor.fetchone()

    hotspot_location = row["location"] if row else "No Data"

    # -----------------------------
  # -----------------------------
# AI Insight 3
# Smart Prediction
# -----------------------------

    if total_reports == 0:

        ai_prediction = "Not enough reports to generate predictions."

    elif high > (medium + low):

        ai_prediction = (
            "🚨 Immediate attention required. High-risk issues dominate the current reports. "
            "Authorities should prioritize emergency inspections."
        )

    elif medium >= high and medium >= low:

        ai_prediction = (
            "⚠️ Preventive maintenance is recommended. Medium-risk issues are increasing "
            "and may become critical if ignored."
        )

    elif low > 0:

        ai_prediction = (
            "✅ Infrastructure appears relatively stable. Continue routine monitoring "
            "to maintain safety standards."
        )

    else:

        ai_prediction = (
            "📊 Additional reports are required before generating reliable predictions."
        )

    # -----------------------------
    # Chart 1 : Severity Distribution
    # -----------------------------
    severity_labels = ["High", "Medium", "Low"]
    severity_data = [high, medium, low]

    # -----------------------------
    # Chart 2 : Category Distribution
    # -----------------------------
    cursor.execute("""
        SELECT category, COUNT(*) AS total
        FROM reports
        GROUP BY category
    """)

    category_rows = cursor.fetchall()

    category_labels = [row["category"] for row in category_rows]
    category_data = [row["total"] for row in category_rows]

    # -----------------------------
    # Chart 3 : Top 5 Hotspots
    # -----------------------------
    cursor.execute("""
        SELECT location, COUNT(*) AS total
        FROM reports
        WHERE location != ''
        GROUP BY location
        ORDER BY total DESC
        LIMIT 5
    """)

    hotspot_rows = cursor.fetchall()

    hotspot_labels = [row["location"] for row in hotspot_rows]
    hotspot_data = [row["total"] for row in hotspot_rows]

    # -----------------------------
    # Chart 4 : Daily Reports
    # -----------------------------
    cursor.execute("""
        SELECT DATE(created_at) AS day,
               COUNT(*) AS total
        FROM reports
        GROUP BY DATE(created_at)
        ORDER BY day
    """)

    trend_rows = cursor.fetchall()

    trend_labels = [row["day"] for row in trend_rows]
    trend_data = [row["total"] for row in trend_rows]

    conn.close()

    return render_template(
        "dashboard.html",

        reports=reports,

        total_reports=total_reports,
        high=high,
        medium=medium,
        low=low,

        highest_category=highest_category,
        hotspot_location=hotspot_location,
        ai_prediction=ai_prediction,

        severity_labels=severity_labels,
        severity_data=severity_data,

        category_labels=category_labels,
        category_data=category_data,

        hotspot_labels=hotspot_labels,
        hotspot_data=hotspot_data,

        trend_labels=trend_labels,
        trend_data=trend_data
    )


# ==============================
# AI Analysis
# ==============================

@app.route("/analyze", methods=["POST"])
def analyze():

    if "image" not in request.files:
        return jsonify({
            "error": "No image uploaded."
        }), 400

    image = request.files["image"]

    if image.filename == "":
        return jsonify({
            "error": "No image selected."
        }), 400

    # Get additional details from the form
    location = request.form.get("location", "").strip()
    description = request.form.get("description", "").strip()

    ext = os.path.splitext(image.filename)[1]

    filename = f"{uuid.uuid4().hex}{ext}"

    save_path = os.path.join("uploads", filename)

    image.save(save_path)

    result = analyze_image(save_path)

    result.setdefault("category", "Other")
    result.setdefault("severity", "Low")
    result.setdefault("department", "Public Works Department")
    result.setdefault("confidence", 0)
    result.setdefault("summary", "No summary available.")
    result.setdefault("recommended_action", "No action defined.")

    save_report(
        result,
        save_path,
        location,
        description
    )

    return jsonify(result)


# ==============================
# Run App
# ==============================

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)