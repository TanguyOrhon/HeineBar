import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from users_db import *

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
        messagebox.showerror("Erreur", f"Le fichier {JSON_FILE} est invalide.")
        return []

def save_articles(articles):
    with open(JSON_FILE, 'w') as f:
        json.dump(articles, f, indent=4)

def main():
    init_user_db()

    root = tk.Tk()
    root.title("Boutique avec utilisateurs")

    # --- Maximiser la fenêtre fenêtrée ---
    root.state('zoomed')

    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TLabel', font=('Segoe UI', 11))
    style.configure('TButton', font=('Segoe UI', 10), padding=6, foreground="black")
    style.configure('TEntry', font=('Segoe UI', 10))
    style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))

    selected_username = tk.StringVar(value="")
    user_options = {}

    # --- Fonctions internes ---
    def update_article_buttons():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        articles = load_articles()
        for article in articles:
            btn = ttk.Button(scroll_frame, text=f"{article['name']} - {article['price']:.2f} €",
                             command=lambda a=article: confirm_purchase(a))
            btn.pack(fill=tk.X, pady=3)

    def add_article():
        name = entry_name.get().strip()
        try:
            price = float(entry_price.get())
        except ValueError:
            messagebox.showerror("Erreur", "Le prix doit être un nombre.")
            return

        if not name:
            messagebox.showerror("Erreur", "Le nom ne peut pas être vide.")
            return

        articles = load_articles()
        articles.append({"name": name, "price": price})
        save_articles(articles)
        entry_name.delete(0, tk.END)
        entry_price.delete(0, tk.END)
        update_article_buttons()
        messagebox.showinfo("Succès", f"Article '{name}' ajouté.")

    def confirm_purchase(article):
        username = selected_username.get()
        if not username:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner un utilisateur.")
            return

        user_id = user_options.get(username)
        if user_id is None:
            messagebox.showerror("Erreur", "Utilisateur invalide.")
            return

        try:
            add_purchase(user_id, article['name'], article['price'])
        except ValueError as e:
            messagebox.showerror("Erreur", str(e))
            return

        messagebox.showinfo("Achat confirmé", f"{article['name']} acheté pour {article['price']:.2f} €.")
        select_user(username)

    def refresh_users():
        menu = user_menu['menu']
        menu.delete(0, 'end')
        users = get_users()
        user_options.clear()
        for uid, name in users:
            user_options[name] = uid
            menu.add_command(label=name, command=lambda n=name: select_user(n))

        if users:
            first_user_name = users[0][1]
            select_user(first_user_name)
        else:
            selected_username.set("")
            user_label.config(text="Aucun utilisateur sélectionné")
            total_label.config(text="Solde : 0.00 €")

    def select_user(username):
        selected_username.set(username)
        uid = user_options.get(username)
        if uid is None:
            user_label.config(text="Utilisateur introuvable")
            total_label.config(text="Solde : 0.00 €")
            return
        total = get_user_balance(uid)
        user_label.config(text=f"Utilisateur sélectionné : {username}")
        total_label.config(text=f"Solde : {total:.2f} €")

    def create_user():
        name = entry_new_user.get().strip()
        balance = entry_solde.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Nom requis.")
            return
        if not balance:
            messagebox.showerror("Erreur", "Solde requis.")
            return
        try:
            balance = float(balance)
        except ValueError:
            messagebox.showerror("Erreur", "Le solde doit être un nombre.")
            return
        if add_user(name, balance):
            entry_new_user.delete(0, tk.END)
            entry_solde.delete(0, tk.END)
            refresh_users()
            messagebox.showinfo("Succès", f"Utilisateur '{name}' ajouté.")
        else:
            messagebox.showerror("Erreur", f"Utilisateur '{name}' existe déjà.")

    def add_balance():
        username = selected_username.get()
        if not username:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner un utilisateur.")
            return

        uid = user_options.get(username)
        if uid is None:
            messagebox.showerror("Erreur", "Utilisateur introuvable.")
            return

        amount_str = entry_balance.get().strip()
        if not amount_str:
            messagebox.showerror("Erreur", "Veuillez saisir un montant.")
            return

        try:
            amount = float(amount_str)
        except ValueError:
            messagebox.showerror("Erreur", "Le montant doit être un nombre.")
            return

        if amount <= 0:
            messagebox.showerror("Erreur", "Le montant doit être supérieur à 0.")
            return

        # Mettre à jour la balance dans la DB
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET balance = balance + ? WHERE id = ?", (amount, uid))
        conn.commit()
        conn.close()

        entry_balance.delete(0, tk.END)
        select_user(username)  # Met à jour l'affichage du solde
        messagebox.showinfo("Succès", f"{amount:.2f} € ajoutés au solde de {username}.")

    # --- Interface ---
    main_frame = ttk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    notebook = ttk.Notebook(main_frame)
    notebook.pack(fill=tk.BOTH, expand=True)

    frame_achats = ttk.Frame(notebook, padding=15)
    notebook.add(frame_achats, text="Achats & Utilisateur")

    frame_creation = ttk.Frame(notebook, padding=15)
    notebook.add(frame_creation, text="Création Article & Utilisateur")

    # --- Widgets Achats & Utilisateur ---
    ttk.Label(frame_achats, text="Sélectionner un utilisateur", style='Header.TLabel').pack(anchor=tk.W)

    user_label = ttk.Label(frame_achats, text="Aucun utilisateur sélectionné", font=('Segoe UI', 12))
    user_label.pack(anchor=tk.W, pady=(0,10))

    user_menu = ttk.OptionMenu(frame_achats, selected_username, None)
    user_menu.pack(anchor=tk.W, pady=(0,15))

    total_label = ttk.Label(frame_achats, text="Solde : 0.00 €", font=('Segoe UI', 11, 'italic'))
    total_label.pack(anchor=tk.W, pady=(0, 15))

    ttk.Label(frame_achats, text="Faire un dépot :", style='Header.TLabel').pack(anchor=tk.W, pady=(10,0))

    entry_balance = ttk.Entry(frame_achats, width=20)
    entry_balance.pack(anchor=tk.W, pady=5)

    btn_add_balance = ttk.Button(frame_achats, text="Ajouter au solde", command=add_balance, width=20)
    btn_add_balance.pack(anchor=tk.W, pady=5)


    ttk.Label(frame_achats, text="Articles disponibles :", style='Header.TLabel').pack(anchor=tk.W)

    canvas = tk.Canvas(frame_achats, borderwidth=0, height=300)
    scroll_frame = ttk.Frame(canvas)
    vsb = ttk.Scrollbar(frame_achats, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    canvas.create_window((0,0), window=scroll_frame, anchor='nw')

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", on_frame_configure)

    # --- Widgets Création Article & Utilisateur ---
    ttk.Label(frame_creation, text="Ajouter un article", style='Header.TLabel').pack(anchor=tk.W, pady=(0,10))

    ttk.Label(frame_creation, text="Nom de l'article:").pack(anchor=tk.W)
    entry_name = ttk.Entry(frame_creation, width=40)
    entry_name.pack(anchor=tk.W, pady=5)

    ttk.Label(frame_creation, text="Prix (€):").pack(anchor=tk.W)
    entry_price = ttk.Entry(frame_creation, width=40)
    entry_price.pack(anchor=tk.W, pady=5)

    btn_add_article = ttk.Button(frame_creation, text="Ajouter l'article", command=add_article, width=40)
    btn_add_article.pack(anchor=tk.W, pady=10)

    ttk.Separator(frame_creation, orient='horizontal').pack(fill=tk.X, pady=20)

    ttk.Label(frame_creation, text="Ajouter un utilisateur", style='Header.TLabel').pack(anchor=tk.W, pady=(0,10))

    ttk.Label(frame_creation, text="Nom de l'utilisateur:").pack(anchor=tk.W)
    entry_new_user = ttk.Entry(frame_creation, width=40)
    entry_new_user.pack(anchor=tk.W, pady=5)

    ttk.Label(frame_creation, text="Dépôt:").pack(anchor=tk.W)
    entry_solde = ttk.Entry(frame_creation, width=40)
    entry_solde.pack(anchor=tk.W, pady=5)

    btn_create_user = ttk.Button(frame_creation, text="Créer utilisateur", command=create_user, width=40)
    btn_create_user.pack(anchor=tk.W, pady=10)

    # --- Initialisation ---
    update_article_buttons()
    refresh_users()

    root.mainloop()

if __name__ == "__main__":
    main()
