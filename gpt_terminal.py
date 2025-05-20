# python gpt_terminal.py

import openai
import os
from config import OPEN_AI_KEY_PATH

# Load your API key (you can also set it via environment variable)
openai.api_key = OPEN_AI_KEY_PATH

def ask_gpt(prompt, model="gpt-o4-mini"):
    response = openai.ChatCompletion.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content'].strip()

if __name__ == "__main__":
    user_input = input("Enter your prompt: ")
    result = ask_gpt(user_input)
    print("\n=== GPT Response ===\n")
    print(result)
