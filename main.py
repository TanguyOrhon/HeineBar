import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from users_db import init_user_db, add_user, get_users, add_purchase, get_user_purchases

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
    root.geometry("900x550")
    root.resizable(False, False)

    style = ttk.Style(root)
    style.theme_use('clam')
    style.configure('TLabel', font=('Segoe UI', 11))
    style.configure('TButton', font=('Segoe UI', 10), padding=6)
    style.configure('TEntry', font=('Segoe UI', 10))
    style.configure('Header.TLabel', font=('Segoe UI', 14, 'bold'))

    selected_user_id = tk.IntVar(value=0)
    user_options = {}

    # --- Fonctions ---

    def update_article_buttons():
        for widget in scroll_frame.winfo_children():
            widget.destroy()
        articles = load_articles()
        for article in articles:
            btn = ttk.Button(scroll_frame, text=f"{article['name']} - {article['price']:.2f} €",
                             command=lambda a=article: add_to_cart(a))
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

    def add_to_cart(article):
        if selected_user_id.get() == 0:
            messagebox.showwarning("Sélection requise", "Veuillez sélectionner un utilisateur.")
            return

        cart_list.insert(tk.END, f"{article['name']} - {article['price']:.2f} €")
        total = get_total() + article['price']
        label_total.config(text=f"Total: {total:.2f} €")

        add_purchase(selected_user_id.get(), article['name'], article['price'])

    def get_total():
        total = 0.0
        for i in range(cart_list.size()):
            try:
                price = float(cart_list.get(i).split('-')[-1].replace('€', '').strip())
                total += price
            except:
                continue
        return total

    def refresh_users():
        menu = user_menu['menu']
        menu.delete(0, 'end')
        users = get_users()
        user_options.clear()
        for uid, name in users:
            user_options[uid] = name
            menu.add_command(label=name, command=lambda v=uid: select_user(v))

        if users:
            first_user_id = users[0][0]
            select_user(first_user_id)
        else:
            selected_user_id.set(0)
            user_label.config(text="Aucun utilisateur sélectionné")
            refresh_cart(0)

    def select_user(uid):
        selected_user_id.set(uid)
        user_label.config(text=f"Utilisateur sélectionné : {user_options.get(uid, 'N/A')}")
        refresh_cart(uid)

    def refresh_cart(uid):
        cart_list.delete(0, tk.END)
        if uid == 0:
            label_total.config(text="Total: 0.00 €")
            return
        purchases = get_user_purchases(uid)
        for name, price in purchases:
            cart_list.insert(tk.END, f"{name} - {price:.2f} €")
        total = sum(price for _, price in purchases)
        label_total.config(text=f"Total: {total:.2f} €")

    def create_user():
        name = entry_new_user.get().strip()
        if not name:
            messagebox.showerror("Erreur", "Nom requis.")
            return
        if add_user(name):
            entry_new_user.delete(0, tk.END)
            refresh_users()
            messagebox.showinfo("Succès", f"Utilisateur '{name}' ajouté.")
        else:
            messagebox.showerror("Erreur", f"Utilisateur '{name}' existe déjà.")

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

    user_menu = ttk.OptionMenu(frame_achats, selected_user_id, None)
    user_menu.pack(anchor=tk.W, pady=(0,15))

    ttk.Label(frame_achats, text="Articles disponibles :", style='Header.TLabel').pack(anchor=tk.W)

    # Scrollable frame pour articles
    canvas = tk.Canvas(frame_achats, borderwidth=0, height=250)
    scroll_frame = ttk.Frame(canvas)
    vsb = ttk.Scrollbar(frame_achats, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)

    vsb.pack(side=tk.RIGHT, fill=tk.Y)
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
    canvas.create_window((0,0), window=scroll_frame, anchor='nw')

    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))
    scroll_frame.bind("<Configure>", on_frame_configure)

    ttk.Separator(frame_achats, orient='horizontal').pack(fill=tk.X, pady=10)

    ttk.Label(frame_achats, text="Panier:", style='Header.TLabel').pack(anchor=tk.W)
    cart_list = tk.Listbox(frame_achats, width=50, height=10, font=('Segoe UI', 10))
    cart_list.pack(fill=tk.BOTH, expand=False, pady=5)

    label_total = ttk.Label(frame_achats, text="Total: 0.00 €", font=('Segoe UI', 12, 'bold'))
    label_total.pack(pady=10)

    # --- Widgets Création Article & Utilisateur ---

    ttk.Label(frame_creation, text="Ajouter un article", style='Header.TLabel').pack(anchor=tk.W, pady=(0,10))

    ttk.Label(frame_creation, text="Nom de l'article:").pack(anchor=tk.W)
    entry_name = ttk.Entry(frame_creation, width=30)
    entry_name.pack(anchor=tk.W, pady=5)

    ttk.Label(frame_creation, text="Prix (€):").pack(anchor=tk.W)
    entry_price = ttk.Entry(frame_creation, width=30)
    entry_price.pack(anchor=tk.W, pady=5)

    btn_add_article = ttk.Button(frame_creation, text="Ajouter l'article", command=add_article)
    btn_add_article.pack(anchor=tk.W, pady=10)

    ttk.Separator(frame_creation, orient='horizontal').pack(fill=tk.X, pady=20)

    ttk.Label(frame_creation, text="Ajouter un utilisateur", style='Header.TLabel').pack(anchor=tk.W, pady=(0,10))

    entry_new_user = ttk.Entry(frame_creation, width=30)
    entry_new_user.pack(anchor=tk.W, pady=5)

    btn_create_user = ttk.Button(frame_creation, text="Créer utilisateur", command=create_user)
    btn_create_user.pack(anchor=tk.W, pady=10)

    # --- Initialisation ---
    update_article_buttons()
    refresh_users()

    root.mainloop()

if __name__ == "__main__":
    main()
