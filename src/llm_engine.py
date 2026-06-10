# Import os to read environment variables
import os

# Import dotenv to load values from the .env file
from dotenv import load_dotenv

# Import OpenAI client using the new OpenAI Python SDK style
from openai import OpenAI


# Load environment variables from .env file
load_dotenv()


# Read OpenAI API key from environment
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


# Stop execution early if API key is missing
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is missing. Please add it to your .env file.")


# Create reusable OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)


# Generate response from OpenAI model
def get_llm_response(prompt, model="gpt-4o-mini", temperature=0):
    # Send user prompt to OpenAI chat completion API
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
        temperature=temperature
    )

    # Return only the text response
    return response.choices[0].message.content


# Run quick test only when this file is executed directly
if __name__ == "__main__":
    # Test simple OpenAI response
    answer = get_llm_response(
        prompt="Explain in one sentence what a warehouse KPI is."
    )

    # Print model answer
    print(answer)