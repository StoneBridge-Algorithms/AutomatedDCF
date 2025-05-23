#!/usr/bin/env python3
import sys
from openai import OpenAI
import config  # your config.py with OPENAI_API_KEY

def main():
    # Initialize the new client
    client = OpenAI(api_key=config.OPENAI_API_KEY)

    # Read the MD&A text from stdin
    print("Paste the Management Discussion & Analysis text below, then press Ctrl-D (Unix/Mac) or Ctrl-Z then Enter (Windows):")
    mdna_text = sys.stdin.read().strip()
    if not mdna_text:
        print("No input detected. Exiting.", file=sys.stderr)
        sys.exit(1)

    try:
        # Use the new client.chat.completions.create() method
        resp = client.chat.completions.create(
            model="gpt-3.5-turbo",      # or "gpt-4"
            temperature=0,              # deterministic
            max_tokens=5,
            messages=[
                {"role": "system", "content": (
                    "You are a classifier. "
                    "Given a company's Management Discussion & Analysis text, "
                    "classify its overall tone as exactly one of: pessimistic, neutral, or optimistic. "
                    "Respond with only that single word."
                )},
                {"role": "user", "content": mdna_text}
            ]
        )
        # Extract the generated label
        label = resp.choices[0].message.content.strip().lower()

        # Enforce only our three labels
        if label not in ("pessimistic", "neutral", "optimistic"):
            print("Error: unexpected response:", label, file=sys.stderr)
            sys.exit(1)

        print(label)

    except Exception as e:
        print("API request failed:", e, file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
