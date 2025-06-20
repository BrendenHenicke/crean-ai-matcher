import os
import json
from openai import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

# Load data from JSON
def load_json_data(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    return data["resumes"], data["job_description"]

# Construct ranking prompt
def build_prompt(resumes, job_description):
    prompt = (
        "You are an AI recruiter. Rank these resumes by how well they fit the following job description.\n\n"
        f"Job Description:\n{job_description}\n\n"
        "Resumes:\n"
    )
    for i, resume in enumerate(resumes, start=1):
        prompt += f"{i}. {resume}\n"
    prompt += (
        "\nProvide a ranking of the top candidates and a brief explanation for each.\n"
        "Output in this format:\n"
        "1. Name - Reason\n"
        "2. Name - Reason\n"
        "..."
    )
    return prompt

# Run the model
def get_ai_ranking(prompt):
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are an AI assistant that ranks resumes for job fit."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

# Main execution
if __name__ == "__main__":
    resumes, job_description = load_json_data("civil_engineer_test_data.json")
    prompt = build_prompt(resumes, job_description)
    ranking = get_ai_ranking(prompt)

    print("\nAI Ranking & Explanation:\n")
    print(ranking)
