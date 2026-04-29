from groq import Groq
import json
import re
from config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)


# 🔥 Clean LLM output safely
def clean_json_output(text: str):
    # Remove markdown code blocks
    text = re.sub(r"```json", "", text)
    text = re.sub(r"```", "", text)

    # Remove leading/trailing junk
    text = text.strip()

    # Extract only JSON part
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        return match.group(0)

    return text


def generate_schema(design: dict):
    prompt = f"""
You are a backend system generator.

Convert the following system design into structured schemas.

Design:
{design}

Return ONLY valid JSON in this format:

{{
  "database": [],
  "api": [],
  "ui": [],
  "auth": []
}}

Rules:
- database: tables with fields (each field MUST have "name" and "type")
- api: endpoints with method, route, request, response
- ui: pages with components (each component must have type and optional props)
- auth: roles with permissions
- STRICT JSON ONLY
- NO markdown
- NO explanation
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    try:
        # 🔥 Clean response
        cleaned = clean_json_output(content)

        # 🔥 Parse JSON safely
        parsed = json.loads(cleaned)

    except Exception as e:
        return {
            "error": "Parsing failed",
            "raw_output": content
        }

    # 🔥 Ensure required keys always exist
    for key in ["database", "api", "ui", "auth"]:
        if key not in parsed or not isinstance(parsed[key], list):
            parsed[key] = []

    return parsed