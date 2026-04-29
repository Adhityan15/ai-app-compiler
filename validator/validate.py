def validate_schema(schema: dict):
    errors = []

    if not isinstance(schema, dict):
        return ["Invalid schema"]

    db_fields = set()

    # ✅ Collect DB fields safely
    for table in schema.get("database", []):
        for field in table.get("fields", []):
            if isinstance(field, dict):
                field_name = field.get("name")
                if field_name:
                    db_fields.add(field_name)

    # ✅ API validation
    for api in schema.get("api", []):
        response = api.get("response", {}).get("schema", {}).get("properties", {})
        if isinstance(response, dict):
            for field in response.keys():
                if field not in db_fields:
                    errors.append(f"API field '{field}' not in DB")

    # ✅ UI validation (SAFE)
    for ui in schema.get("ui", []):
        for comp in ui.get("components", []):
            props = comp.get("props", {})

            if comp.get("type") == "list":
                items = props.get("items", [])

                if isinstance(items, list) and len(items) > 0:
                    for field in items[0].keys():
                        if field not in db_fields:
                            errors.append(f"UI field '{field}' not in DB")

    return errors