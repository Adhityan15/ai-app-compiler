def refine_schema(schema: dict):
    # Simple refinement: ensure naming consistency
    for table in schema.get("database", []):
        table["name"] = table["name"].lower()

    return schema