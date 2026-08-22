# users_db.py
import sqlite3

DB_FILE = "users.db"

def init_user_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Table des utilisateurs mise à jour
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            firstname TEXT NOT NULL,
            phone_number TEXT NOT NULL,
            balance REAL DEFAULT 0.0
        )
    """)

    # Table des achats
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS purchases (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            item_name TEXT,
            item_price REAL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)
    conn.commit()
    conn.close()

def add_user(name, firstname, phone_number, initial_balance=0.0):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (name, firstname, phone_number, balance) VALUES (?, ?, ?, ?)", 
                       (name, firstname, phone_number, initial_balance))
        conn.commit()
        return True
    except sqlite3.Error:
        return False
    finally:
        conn.close()

def get_users():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    # Retourne id, name, firstname
    cursor.execute("SELECT id, name, firstname FROM users")
    users = cursor.fetchall()
    conn.close()
    return users

def add_purchase(user_id, item_name, item_price):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Vérifier le solde actuel
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    
    if result is None:
        conn.close()
        raise ValueError("Utilisateur introuvable")

    current_balance = result[0]

    if current_balance < item_price:
        conn.close()
        raise ValueError("Solde insuffisant pour effectuer l'achat")

    # Déduire le prix de l'article
    new_balance = current_balance - item_price
    cursor.execute("UPDATE users SET balance = ? WHERE id = ?", (new_balance, user_id))

    # Ajouter l'achat
    cursor.execute("INSERT INTO purchases (user_id, item_name, item_price) VALUES (?, ?, ?)",
                   (user_id, item_name, item_price))

    conn.commit()
    conn.close()


def get_user_purchases(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT item_name, item_price FROM purchases WHERE user_id = ?", (user_id,))
    purchases = cursor.fetchall()
    conn.close()
    return purchases

def get_total_spent_by_user(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(item_price) FROM purchases WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result[0] is not None else 0.0

def get_user_balance(user_id):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT balance FROM users WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result is not None else 0.0
