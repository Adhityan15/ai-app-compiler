from groq import Groq
import json
import re
from config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)


def design_system(intent: dict):
    prompt = f"""
You are a senior system architect.

Convert the given intent into a STRICT system design.

Intent:
{intent}

Return ONLY valid JSON in this format:

{{
    "entities": [
        {{
            "entity": "",
            "fields": []
        }}
    ],
    "modules": [],
    "user_flows": [],
    "relationships": []
}}

Rules:
- NO descriptions
- ONLY structured data
- Fields must be realistic (id, email, etc.)
- Ensure output is usable for database + API generation
- No markdown
- No explanation
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    # 🔥 Clean markdown
    cleaned = re.sub(r"```json|```", "", content).strip()

    # 🔥 Extract JSON
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)

    if not match:
        return {"error": "No JSON found", "raw_output": content}

    json_str = match.group(0)

    try:
        parsed = json.loads(json_str)
    except:
        return {"error": "JSON parsing failed", "raw_output": content}

    # 🔥 Basic validation
    keys = ["entities", "modules", "user_flows", "relationships"]

    for key in keys:
        if key not in parsed:
            parsed[key] = []

    return parsed