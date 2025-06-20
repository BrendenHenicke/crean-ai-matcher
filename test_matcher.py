# Step 3: Start building the AI matching logic

import os
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=api_key)

# Sample job description (you'll replace this with real input later)
job_description = "Looking for a systems engineer with aerospace experience, skilled in Python, C++, and project management, preferably with NASA or defense background."

# Sample engineer database (in reality, this would be a database or spreadsheet)
engineers = [
    {
        "name": "Alice Johnson",
        "skills": "Python, aerospace systems, NASA, project management",
        "experience": "8 years with NASA on satellite systems."
    },
    {
        "name": "Brian Lee",
        "skills": "C++, embedded systems, automotive industry",
        "experience": "5 years at Tesla, no aerospace experience."
    },
    {
        "name": "Carla Ramirez",
        "skills": "Python, C++, aerospace, defense, project management",
        "experience": "10 years in defense contracting with Raytheon."
    }
]

# Create the system message
system_prompt = """
You are an expert technical recruiter. Match the best engineers from the list to the job description provided. Rank the top 5 and explain why each was ranked where they are.
"""

# Create the user prompt from job and engineers
engineer_data = "\n".join([f"Name: {e['name']}\nSkills: {e['skills']}\nExperience: {e['experience']}" for e in engineers])
user_prompt = f"Job Description: {job_description}\n\nEngineer Database:\n{engineer_data}"

# Get AI response
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)

# Output the response
print(response.choices[0].message.content)
