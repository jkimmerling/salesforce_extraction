import os
from dotenv import load_dotenv

# Load variables from .env file
load_dotenv()


def get_credentials(integration):
    return {
        f"{integration}_password": os.environ[f"{integration.upper()}_PASSWORD"],
        f"{integration}_username": os.environ[f"{integration.upper()}_USERNAME"],
        f"{integration}_security_token": os.environ[f"{integration.upper()}_SECURITY_TOKEN"]
    }


def get_nested_values(key, data):
    values = [d[key] for d in data]
    return values
