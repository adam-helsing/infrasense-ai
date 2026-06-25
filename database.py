import sqlite3

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

        image_path TEXT

    )
    """)

    conn.commit()
    conn.close()


def save_report(data, image_path):

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO reports(

        category,
        severity,
        department,
        confidence,
        summary,
        recommended_action,
        image_path

    )

    VALUES(?,?,?,?,?,?,?)

    """,

    (

        data["category"],
        data["severity"],
        data["department"],
        data["confidence"],
        data["summary"],
        data["recommended_action"],
        image_path

    ))

    conn.commit()
    conn.close()