import os


def lambda_handler(event, context):
    valid_api_keys = {
        key.strip()
        for key in os.environ["VALID_API_KEYS"].split(",")
        if key.strip()
    }
    headers = event.get("headers") or {}
    api_key = next(
        (
            value
            for name, value in headers.items()
            if name.lower() == "x-api-key"
        ),
        None,
    )

    return {"isAuthorized": api_key in valid_api_keys}
