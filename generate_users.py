"""
This script generates 100 random users to populate our database. Usernames, first names, and last names are generated 
from randomuser.me. randomuser.me also sources pictures from the authorized images on uifaces.com. While uifaces.com 
is no longer maintained, more info can be found at https://web.archive.org/web/20160811185628/http://uifaces.com/faq
"""

import requests
import json
import os
import time

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def get_random_users(n=100):
    url = f"https://randomuser.me/api/?results={n}"
    while True:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()
            return data["results"]
        except requests.exceptions.RequestException as e:
            print(f"❌ API error: {e}. Retrying in 5 seconds...")
            time.sleep(5)

def format_users(raw_users):
    users = {}
    for i, u in enumerate(raw_users):
        user_id = i + 1  # or use UUIDs if you prefer
        users[user_id] = {
            "username": u["login"]["username"],
            "firstName": u["name"]["first"],
            "lastName": u["name"]["last"],
            "profilePic": u["picture"]["large"],
        }
    return users

def main():
    print("🎲 Generating random users...")
    raw = get_random_users(100)
    users = format_users(raw)
    print(users[1])

    with open(f"{DATA_DIR}/users.json", "w") as f:
        json.dump(users, f, indent=2)
    
    print(f"✅ Saved {len(users)} users to users.json")

if __name__ == "__main__":
    main()
