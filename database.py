import sqlite3
from datetime import datetime


def init_db():

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS reports (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    category TEXT,
    severity TEXT,
    department TEXT,
    confidence TEXT,
    summary TEXT,
    recommended_action TEXT,

    location TEXT,
    description TEXT,

    image_path TEXT,

    status TEXT DEFAULT 'Pending',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

    conn.commit()
    conn.close()


def save_report(data, image_path, location="", description=""):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO reports (

            category,
            severity,
            department,
            confidence,
            summary,
            recommended_action,

            location,
            description,

            image_path,

            status

        )

        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            data.get("category"),
            data.get("severity"),
            data.get("department"),
            data.get("confidence"),
            data.get("summary"),
            data.get("recommended_action"),

            location,
            description,

            image_path,

            "Pending"
        ),
    )

    conn.commit()
    conn.close()