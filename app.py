import streamlit as st
import os
import json
import sqlite3
import uuid
from datetime import datetime
from collections import Counter
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from langchain.embeddings import OpenAIEmbeddings
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from feedback_db import init_db, insert_feedback

import docx2txt
import PyPDF2
import pandas as pd

# --- Initialize database and environment ---
init_db()
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)
embedding_model = OpenAIEmbeddings(openai_api_key=api_key)

st.title("Crean AI Engineer Matcher")

# --- Upload Engineer Resumes ---
st.subheader("Step 1: Upload Engineer Resumes Database")
resumes_file = st.file_uploader(
    "Upload resumes file (JSON, TXT, DOCX, PDF, XLSX)",
    type=["json", "txt", "docx", "pdf", "xlsx"],
    key="resumes"
)

# --- Upload Job Descriptions ---
st.subheader("Step 2: Upload Job Description")
job_file = st.file_uploader(
    "Upload job description file (JSON, TXT, DOCX, PDF, XLSX)",
    type=["json", "txt", "docx", "pdf", "xlsx"],
    key="job"
)

job_description = None
resumes = []

# --- Extraction Function ---
def extract_text_from_file(uploaded_file):
    file_type = uploaded_file.name.split(".")[-1].lower()
    if file_type == "pdf":
        reader = PyPDF2.PdfReader(uploaded_file)
        return "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
    elif file_type == "docx":
        return docx2txt.process(uploaded_file)
    elif file_type == "txt":
        return uploaded_file.read().decode("utf-8")
    elif file_type == "xlsx":
        df = pd.read_excel(uploaded_file)
        return df.to_string(index=False)
    elif file_type == "json":
        return uploaded_file.read().decode("utf-8")
    else:
        return ""

# --- Handle job description file ---
if job_file:
    try:
        jd_text = extract_text_from_file(job_file)
        if job_file.name.endswith("json"):
            job_data = json.loads(jd_text)
            job_description = job_data.get("job_description", jd_text)
        else:
            job_description = jd_text
    except Exception as e:
        st.error(f"Failed to process job description file: {e}")

# --- Handle resumes file ---
if resumes_file:
    try:
        res_text = extract_text_from_file(resumes_file)
        if resumes_file.name.endswith("json"):
            res_data = json.loads(res_text)
            resumes = res_data.get("resumes", [])
        else:
            resumes = [
                {"name": f"Candidate {i+1}", "skills": "", "experience": chunk.strip()}
                for i, chunk in enumerate(res_text.split("\n\n")) if chunk.strip()
            ]
    except Exception as e:
        st.error(f"Failed to process resumes file: {e}")

# --- Manual Entry Fallback ---
manual_input = st.text_area("Or paste job description and engineer details manually")
if manual_input:
    job_description = manual_input

# --- Simulated Engineer Database if none uploaded ---
if not resumes:
    resumes = [
        {"name": "Alice", "skills": "Python, SQL", "experience": "3 years in data analysis"},
        {"name": "Bob", "skills": "Java, AWS", "experience": "5 years in cloud infrastructure"},
        {"name": "Charlie", "skills": "C++, robotics", "experience": "2 years in embedded systems"},
        {"name": "Dana", "skills": "JavaScript, React", "experience": "4 years in frontend dev"},
        {"name": "Eli", "skills": "Python, Machine Learning", "experience": "6 years in AI"}
    ]

# --- Proceed if job description is available ---
if job_description:
    job_embedding = embedding_model.embed_query(job_description)
    resume_embeddings = []
    for resume in resumes:
        combined_text = f"{resume['name']}\nSkills: {resume['skills']}\nExperience: {resume['experience']}"
        vector = embedding_model.embed_query(combined_text)
        resume_embeddings.append((resume, vector))

    scored_resumes = [
        (resume, cosine_similarity([job_embedding], [vector])[0][0])
        for resume, vector in resume_embeddings
    ]

    top_5 = sorted(scored_resumes, key=lambda x: x[1], reverse=True)[:5]
    ranked_text = "\n\n".join(
        [f"Name: {r['name']}\nSkills: {r['skills']}\nExperience: {r['experience']}\nSimilarity Score: {round(s, 4)}" for r, s in top_5]
    )

    system_msg = SystemMessage(content="You are an expert recruiter. Explain why these 5 engineers were selected based on the job description.")
    user_msg = HumanMessage(content=f"Job Description:\n{job_description}\n\nTop 5 Engineers:\n{ranked_text}")
    response = llm.invoke([system_msg, user_msg])
    result_text = response.content

    st.subheader("Top Matches:")
    st.write(result_text)

    st.subheader("Provide Feedback for Each Candidate")
    candidate_names = [line.split('.', 1)[1].split(':', 1)[0].strip() for line in result_text.splitlines() if line.strip().startswith(tuple(str(i) for i in range(1, 6)))]

    feedback_list = []
    for name in candidate_names:
        st.markdown(f"### Feedback for {name}")
        rating = st.slider(f"Rate {name} (1=Poor, 5=Excellent)", 1, 5, key=f"rating_{name}")
        notes = st.text_area(f"Notes for {name}", key=f"notes_{name}")
        feedback_list.append({'name': name, 'rating': rating, 'notes': notes})

    st.subheader("Overall Feedback")
    user_feedback = st.text_area("Any other comments or suggestions?")

    if st.button("Submit Feedback"):
        feedback_entry = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.now().isoformat(),
            "job_description": job_description,
            "resumes": resumes,
            "ai_output": result_text,
            "per_candidate_feedback": feedback_list,
            "overall_feedback": user_feedback
        }
        insert_feedback(feedback_entry)
        st.success("Feedback submitted! Thank you.")

    # --- Sidebar Summary ---
    conn = sqlite3.connect("feedback.db")
    c = conn.cursor()
    st.sidebar.subheader("\U0001F4CA Feedback Summary")

    c.execute("SELECT COUNT(*) FROM feedback")
    total = c.fetchone()[0]
    c.execute("SELECT AVG(rating) FROM candidate_feedback")
    avg_rating = round(c.fetchone()[0] or 0, 2)
    c.execute("SELECT overall_feedback FROM feedback")
    all_comments = " ".join([row[0] for row in c.fetchall()])
    keyword_counts = Counter(all_comments.lower().split())
    common_keywords = ", ".join([word for word, _ in keyword_counts.most_common(5)])

    st.sidebar.markdown(f"**Total Feedback Entries:** {total}")
    st.sidebar.markdown(f"**Avg Rating:** {avg_rating}")
    st.sidebar.markdown(f"**Top Keywords:** {common_keywords}")

    c.execute("SELECT overall_feedback FROM feedback ORDER BY timestamp DESC LIMIT 3")
    st.sidebar.markdown("**Latest Comments:**")
    for row in c.fetchall():
        st.sidebar.info(row[0])

    conn.close()

else:
    st.info("Please upload at least one file or enter job description text to proceed.")


