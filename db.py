import sqlite3

def init_db():
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_description TEXT,
            resumes TEXT,
            ai_output TEXT,
            notes TEXT,
            rating INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_feedback(job_description, resumes, ai_output, notes, rating):
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    c.execute('''
        INSERT INTO feedback (job_description, resumes, ai_output, notes, rating)
        VALUES (?, ?, ?, ?, ?)
    ''', (job_description, resumes, ai_output, notes, rating))
    conn.commit()
    conn.close()
