import os
from dotenv import load_dotenv

load_dotenv()

# config for login to webapp
APP_USERNAME = os.getenv("APP_USERNAME", "")
APP_PASSWORD_HASH = os.getenv("APP_PASSWORD_HASH", "")
SESSION_SECRET_KEY = os.getenv("SESSION_SECRET_KEY", "")

if not APP_USERNAME or not APP_PASSWORD_HASH or not SESSION_SECRET_KEY:
    raise RuntimeError(
        "Missing required environment variables: "
        "APP_USERNAME, APP_PASSWORD_HASH, SESSION_SECRET_KEY"
    )

# config for aws services
DYNAMODB_TABLE_NAME = os.getenv("DYNAMODB_TABLE_NAME", "")
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "")
AWS_REGION = os.getenv("AWS_REGION", "")
