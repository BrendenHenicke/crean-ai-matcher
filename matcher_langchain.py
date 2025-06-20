
import os
import json
import re
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage
from dotenv import load_dotenv
from db import init_db, insert_job, insert_resume, insert_ranking  # 🔧 DB functions

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
llm = ChatOpenAI(model="gpt-4", openai_api_key=api_key)

# Initialize the database
init_db()

# Load data from JSON file
def load_json_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data["resumes"], data["job_description"]

# Load your test data
resumes, job_description = load_json_data("civil_job_test.json")

# Insert the job description into DB
job_id = insert_job(job_description)

# Insert resumes into DB and collect resume IDs
resume_ids = []
for e in resumes:
    resume_id = insert_resume(e["name"], e["skills"], e["experience"])
    resume_ids.append(resume_id)

# Format resumes into string
engineer_data = "\n\n".join(
    [f"Name: {e['name']}\nSkills: {e['skills']}\nExperience: {e['experience']}" for e in resumes]
)

# Create LangChain messages
system_msg = SystemMessage(
    content="You are an expert technical recruiter. Match the best engineers from the list to the job description provided. Rank the top 5 and explain why each was ranked where they are."
)

user_msg = HumanMessage(
    content=f"Job Description: {job_description}\n\nEngineer Database:\n{engineer_data}"
)

# Invoke LLM and get response
response = llm.invoke([system_msg, user_msg])
print(response.content)

# Parse the AI output and store rankings
pattern = r"\d+\.\s+(.*?):\s+(.*)"
matches = re.findall(pattern, response.content)

for idx, (name, reason) in enumerate(matches):
    for i, resume in enumerate(resumes):
        if name.strip().lower() in resume["name"].lower():
            insert_ranking(job_id, resume_ids[i], idx + 1, reason)
            break
