# test_env.py
from dotenv import load_dotenv
import os

load_dotenv()

print("Testing .env file:")
print(f"KV_URL exists: {bool(os.getenv('KV_URL'))}")
print(f"KV_REST_API_URL: {os.getenv('KV_REST_API_URL')}")
print(f"KV_REST_API_TOKEN exists: {bool(os.getenv('KV_REST_API_TOKEN'))}")