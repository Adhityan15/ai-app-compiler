from fastapi import FastAPI
from fastapi.responses import HTMLResponse
import os

from pipeline.intent import extract_intent
from pipeline.design import design_system
from pipeline.schema import generate_schema
from validator.validate import validate_schema
from validator.repair import repair_schema

from pipeline.refine import refine_schema
from pipeline.executor import simulate_execution

app = FastAPI()

# 🔥 Metrics
total_requests = 0
successful_requests = 0


@app.get("/")
def home():
    return {"message": "AI System Running 🚀"}


@app.post("/generate")
def generate(user_input: str):
    global total_requests, successful_requests

    try:
        total_requests += 1

        # 🔹 Stage 1
        intent = extract_intent(user_input)

        # 🔹 Stage 2
        design = design_system(intent)

        # 🔹 Stage 3
        schema = generate_schema(design)

        # 🔒 Safety check
        if not isinstance(schema, dict) or "database" not in schema:
            return {
                "error": "Schema generation failed",
                "details": schema
            }

        # 🔹 Stage 4: refine + simulate execution
        schema = refine_schema(schema)
        execution = simulate_execution(schema)

        # 🔹 Stage 5: validation
        errors = validate_schema(schema)
        if not isinstance(errors, list):
            errors = []

        # 🔹 Stage 6: repair
        if errors:
            schema = repair_schema(schema, errors)

        # 🔹 Metrics
        if len(errors) == 0:
            successful_requests += 1

        return {
            "input": user_input,
            "intent": intent,
            "design": design,
            "schema": schema,
            "execution": execution,
            "validation_errors": errors,
            "meta": {
                "valid": len(errors) == 0,
                "error_count": len(errors),
                "status": "success" if len(errors) == 0 else "repaired"
            },
            "metrics": {
                "total_requests": total_requests,
                "success_rate": round((successful_requests / total_requests) * 100, 2)
            }
        }

    except Exception as e:
        return {
            "error": "Internal error",
            "message": str(e)
        }


# 🌐 Serve UI from separate file
@app.get("/app", response_class=HTMLResponse)
def web_ui():
    try:
        file_path = os.path.join(os.path.dirname(__file__), "ui.html")
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception as e:
        return f"<h2>UI Load Error</h2><p>{str(e)}</p>"