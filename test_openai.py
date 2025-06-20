import os
from openai import OpenAI
from dotenv import load_dotenv

# Load the environment variables from .env file
load_dotenv()

# Grab the API key from environment
api_key = os.getenv("OPENAI_API_KEY")

# Initialize the OpenAI client with your key
client = OpenAI(api_key=api_key)

# Send a test request
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "What is the capital of Texas?"}
    ]
)

# Print the AI's reply
print(response.choices[0].message.content)


