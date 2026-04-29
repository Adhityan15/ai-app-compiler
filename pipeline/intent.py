from groq import Groq
import json
import re
from config import GROQ_API_KEY, MODEL

client = Groq(api_key=GROQ_API_KEY)


def extract_intent(user_input: str):
    prompt = f"""
Extract structured intent from this app request.

Input:
{user_input}

Return ONLY valid JSON:

{{
    "app_name": "",
    "features": ["feature1", "feature2"],
    "roles": ["role1", "role2"],
    "assumptions": []
}}

Rules:
- features MUST be a list of simple strings (no objects)
- roles MUST be a list of simple strings (no objects)
- no descriptions
- no markdown
- no explanation
"""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    content = response.choices[0].message.content.strip()

    # 🔥 remove markdown if model adds it
    cleaned = re.sub(r"```json|```", "", content).strip()

    # 🔥 extract JSON only
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if not match:
        return {"error": "No JSON found", "raw_output": content}

    json_str = match.group(0)

    try:
        parsed = json.loads(json_str)
    except:
        return {"error": "JSON parsing failed", "raw_output": content}

    # 🔥 enforce required keys
    parsed.setdefault("app_name", "")
    parsed.setdefault("features", [])
    parsed.setdefault("roles", [])
    parsed.setdefault("assumptions", [])

    # 🔥 normalize features → list of strings
    normalized_features = []
    for f in parsed["features"]:
        if isinstance(f, dict) and "name" in f:
            normalized_features.append(str(f["name"]).lower())
        else:
            normalized_features.append(str(f).lower())
    parsed["features"] = normalized_features

    # 🔥 normalize roles → list of strings
    normalized_roles = []
    for r in parsed["roles"]:
        if isinstance(r, dict) and "name" in r:
            normalized_roles.append(str(r["name"]).lower())
        else:
            normalized_roles.append(str(r).lower())
    parsed["roles"] = normalized_roles

    return parsed