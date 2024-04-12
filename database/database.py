import json
import os

DATABASE_PATH = "database/database.json"

def load_database():
    if os.path.exists(DATABASE_PATH):
        with open(DATABASE_PATH, "r") as file:
            return json.load(file)
    return {}

def save_database(database):
    with open(DATABASE_PATH, "w") as file:
        json.dump(database, file, indent=4)
