# check_github.py
import os
import requests
from dotenv import load_dotenv

load_dotenv()

token = os.environ.get("GH_TOKEN")
print("Token found:", bool(token), "| length:", len(token) if token else 0)

r = requests.get(
    "https://api.github.com/user",
    headers={"Authorization": f"Bearer {token}",
             "Accept": "application/vnd.github+json"},
    timeout=10,
)
print("Status:", r.status_code)
print("Login:", r.json().get("login"))
print("Rate limit remaining:", r.headers.get("X-RateLimit-Remaining"))