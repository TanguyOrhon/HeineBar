import json
import os
import sqlite3
from src.db import users_db

JSON_FILE = 'articles.json'

def load_articles():
    if not os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'w') as f:
            json.dump([], f)
    try:
        with open(JSON_FILE, 'r') as f:
            data = f.read().strip()
            if not data:
                return []
            return json.loads(data)
    except json.JSONDecodeError:
        return []

def save_articles(articles):
    with open(JSON_FILE, 'w') as f:
        json.dump(articles, f, indent=4)

def add_article_to_json(name, price):
    articles = load_articles()
    articles.append({"name": name, "price": price})
    save_articles(articles)

def add_balance_to_db(amount, user_id):
    conn = sqlite3.connect(users_db.DB_FILE)
    cursor = conn.cursor()
    cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, user_id))
    conn.commit()
    conn.close()

def import_users_from_csv(file_path):
    import csv
    count = 0
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            if users_db.add_user(row['name'], row['firstname'], row['phone_number']):
                count += 1
    return count
