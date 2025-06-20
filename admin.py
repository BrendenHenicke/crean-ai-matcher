import streamlit as st
import sqlite3
import pandas as pd
import json

# --- Connect to the SQLite database ---
conn = sqlite3.connect("feedback.db")

# --- Load feedback entries ---
query = "SELECT * FROM feedback"
df = pd.read_sql_query(query, conn)

st.title("🧠 Crean AI Matcher - Admin Dashboard")
st.write("Review all feedback submitted through the matcher app.")

# Show columns to verify structure
st.write("Columns in feedback table:", df.columns.tolist())

# Check if per_candidate_feedback column exists
if "per_candidate_feedback" not in df.columns:
    st.error("No per_candidate_feedback column found in feedback table.")
    st.stop()

# Parse and flatten per_candidate_feedback JSON for each feedback entry
candidate_feedback_records = []

for idx, row in df.iterrows():
    try:
        per_candidate_list = json.loads(row["per_candidate_feedback"])
        for feedback in per_candidate_list:
            candidate_feedback_records.append({
                "feedback_id": row["id"],
                "timestamp": row["timestamp"],
                "job_description": row["job_description"],
                "candidate_name": feedback.get("name", ""),
                "rating": feedback.get("rating", None),
                "notes": feedback.get("notes", ""),
                "overall_feedback": row.get("overall_feedback", "")
            })
    except Exception as e:
        st.warning(f"Skipping feedback id {row['id']} due to parsing error: {e}")

# Create DataFrame from flattened candidate feedback
cand_df = pd.DataFrame(candidate_feedback_records)

if cand_df.empty:
    st.info("No candidate feedback records found.")
    st.stop()

# --- Sidebar filters ---
st.sidebar.header("🔎 Filter Feedback")

job_descriptions = ["All"] + sorted(cand_df["job_description"].dropna().unique().tolist())
selected_job = st.sidebar.selectbox("Filter by Job Description", job_descriptions)

candidate_names = ["All"] + sorted(cand_df["candidate_name"].dropna().unique().tolist())
selected_candidate = st.sidebar.selectbox("Filter by Candidate", candidate_names)

selected_rating = st.sidebar.slider("Minimum Rating", 1, 5, 1)

# Apply filters
filtered = cand_df.copy()
if selected_job != "All":
    filtered = filtered[filtered["job_description"] == selected_job]

if selected_candidate != "All":
    filtered = filtered[filtered["candidate_name"] == selected_candidate]

filtered = filtered[filtered["rating"].fillna(0) >= selected_rating]

# Display filtered results
st.subheader("📋 Candidate Feedback Records")
st.dataframe(filtered, use_container_width=True)

# Export filtered data as CSV
csv = filtered.to_csv(index=False).encode("utf-8")
st.download_button("Download CSV", csv, "filtered_feedback.csv", "text/csv")

# Close DB connection
conn.close()

