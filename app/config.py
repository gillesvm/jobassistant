import os
from dotenv import load_dotenv

load_dotenv()

APP_USERNAME = os.getenv("APP_USERNAME", "")
APP_PASSWORD = os.getenv("APP_PASSWORD", "")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "")

if not APP_USERNAME or not APP_PASSWORD or not SESSION_SECRET_KEY:
    raise RuntimeError(
        "Missing required environment variables: "
        "APP_USERNAME, APP_PASSWORD, SESSION_SECRET_KEY"
    )
