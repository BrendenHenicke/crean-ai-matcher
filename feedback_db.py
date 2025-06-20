import sqlite3
from datetime import datetime

def init_db():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    
    # Table for overall feedback
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY,
            timestamp TEXT,
            job_description TEXT,
            resumes_json TEXT,
            ai_output TEXT,
            overall_feedback TEXT
        )
    ''')

    # Table for per-candidate ratings
    c.execute('''
        CREATE TABLE IF NOT EXISTS candidate_feedback (
            feedback_id TEXT,
            name TEXT,
            rating INTEGER,
            notes TEXT,
            FOREIGN KEY (feedback_id) REFERENCES feedback(id)
        )
    ''')

    conn.commit()
    conn.close()

def insert_feedback(feedback_entry):
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()

    # Insert overall feedback
    c.execute('''
        INSERT INTO feedback (id, timestamp, job_description, resumes_json, ai_output, overall_feedback)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (
        feedback_entry["id"],
        feedback_entry["timestamp"],
        feedback_entry["job_description"],
        str(feedback_entry["resumes"]),
        feedback_entry["ai_output"],
        feedback_entry["overall_feedback"]
    ))

    # Insert per-candidate feedback
    for candidate in feedback_entry["per_candidate_feedback"]:
        c.execute('''
            INSERT INTO candidate_feedback (feedback_id, name, rating, notes)
            VALUES (?, ?, ?, ?)
        ''', (
            feedback_entry["id"],
            candidate["name"],
            candidate["rating"],
            candidate["notes"]
        ))

    conn.commit()
    conn.close()
