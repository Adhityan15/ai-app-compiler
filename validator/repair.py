def repair_schema(schema: dict, errors: list):

    for error in errors:
        if "API field" in error:
            field = error.split("'")[1]

            for api in schema.get("api", []):
                response = api.get("response", {}).get("200", {}).get("body")

                if isinstance(response, dict):
                    response.pop(field, None)

                elif isinstance(response, list) and response:
                    response[0].pop(field, None)

    return schema