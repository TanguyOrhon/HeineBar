import tkinter as tk
from src.ui.ui import HeineBarUI
from src.logic import logic
from src.db import users_db

def main():
    users_db.init_user_db()
    
    root = tk.Tk()
    
    callbacks = {
        'get_articles': logic.load_articles,
        'add_article': logic.add_article_to_json,
        'get_users': users_db.get_users,
        'add_user': users_db.add_user,
        'get_balance': users_db.get_user_balance,
        'add_purchase': users_db.add_purchase,
        'add_balance': logic.add_balance_to_db,
        'import_csv': logic.import_users_from_csv
    }
    
    app = HeineBarUI(root, callbacks)
    root.mainloop()

if __name__ == "__main__":
    main()
