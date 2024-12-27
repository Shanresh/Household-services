from dotenv import load_dotenv
import os

# Load .env file
load_dotenv(dotenv_path="Environ.env")

# Print environment variables
print(f"SECRET_KEY: {os.getenv('SECRET_KEY')}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")