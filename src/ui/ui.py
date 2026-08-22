import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog
from src.components.search_bar import UserSearchBar

class HeineBarUI:
    def __init__(self, root, callbacks):
        self.root = root
        self.root.title("HeineBar - Système de Caisse")
        try: self.root.state('zoomed')
        except tk.TclError: self.root.attributes('-zoomed', True)

        self.cbs = callbacks
        self.BG_COLOR, self.CARD_BG = "#121212", "#1e1e1e"
        self.TEXT_COLOR, self.TEXT_MUTED = "#ffffff", "#aaaaaa"
        self.HEINEKEN_GREEN = "#008226"

        self.root.configure(bg=self.BG_COLOR)
        self.style = ttk.Style(self.root)
        self.style.theme_use('clam')
        self.configure_styles()

        self.all_users = []
        self.create_widgets()
        self.refresh_users()
        self.update_article_buttons()

    def configure_styles(self):
        self.style.configure('TFrame', background=self.BG_COLOR)
        self.style.configure('TNotebook', background=self.BG_COLOR, borderwidth=0)
        self.style.configure('TNotebook.Tab', background=self.CARD_BG, foreground=self.TEXT_MUTED, font=('Segoe UI', 11, 'bold'), padding=[20, 8], borderwidth=0)
        self.style.map('TNotebook.Tab', background=[('selected', "#2a2a2a")], foreground=[('selected', self.TEXT_COLOR)])
        self.style.configure('TLabel', background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=('Segoe UI', 11))
        self.style.configure('Header.TLabel', background=self.BG_COLOR, foreground=self.HEINEKEN_GREEN, font=('Segoe UI', 15, 'bold'))
        self.style.configure('User.TLabel', background=self.BG_COLOR, foreground=self.TEXT_COLOR, font=('Segoe UI', 13, 'bold'))
        self.style.configure('Total.TLabel', background=self.BG_COLOR, foreground="#ffb000", font=('Segoe UI', 16, 'bold'))
        self.style.configure('Sub.TLabel', background=self.BG_COLOR, foreground=self.TEXT_MUTED, font=('Segoe UI', 10, 'italic'))
        self.style.configure('TButton', background=self.HEINEKEN_GREEN, foreground='#ffffff', font=('Segoe UI', 11, 'bold'), padding=8)
        self.style.configure('Gold.TButton', background="#ffb000", foreground='#000000', font=('Segoe UI', 11, 'bold'), padding=8)
        self.style.configure('TEntry', fieldbackground=self.CARD_BG, foreground=self.TEXT_COLOR, padding=8, insertcolor='white')

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        frame_achats = ttk.Frame(self.notebook, padding=25)
        self.notebook.add(frame_achats, text="Achats & Utilisateur")
        left_panel = ttk.Frame(frame_achats)
        left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        right_panel = ttk.Frame(frame_achats)
        right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))

        ttk.Label(left_panel, text="Rechercher (Prénom ou Nom) :", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))
        self.search_bar = UserSearchBar(left_panel, [], self.on_user_selected, font=('Segoe UI', 11))
        self.search_bar.pack(anchor=tk.W, pady=(0, 20), fill=tk.X)
        self.user_label = ttk.Label(left_panel, text="Aucun utilisateur sélectionné", style='User.TLabel')
        self.user_label.pack(anchor=tk.W, pady=(0, 5))
        self.total_label = ttk.Label(left_panel, text="Solde : 0.00 €", style='Total.TLabel')
        self.total_label.pack(anchor=tk.W, pady=(0, 25))
        
        ttk.Separator(left_panel, orient='horizontal').pack(fill=tk.X, pady=15)
        ttk.Label(left_panel, text="Faire un dépôt :", style='Header.TLabel').pack(anchor=tk.W, pady=(10, 10))
        self.entry_balance = ttk.Entry(left_panel)
        self.entry_balance.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)
        ttk.Button(left_panel, text="Ajouter au solde", command=self.handle_add_balance).pack(anchor=tk.W, fill=tk.X)

        ttk.Label(right_panel, text="Articles disponibles :", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 10))
        self.canvas = tk.Canvas(right_panel, borderwidth=0, highlightthickness=0, bg=self.BG_COLOR)
        self.scroll_frame = ttk.Frame(self.canvas)
        vsb = ttk.Scrollbar(right_panel, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor='nw')
        self.canvas.bind('<Configure>', lambda e: self.canvas.itemconfig(self.canvas_window, width=e.width))
        self.scroll_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        frame_creation = ttk.Frame(self.notebook, padding=25)
        self.notebook.add(frame_creation, text="Gestion & Administration")
        create_left_panel = ttk.Frame(frame_creation)
        create_left_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        create_right_panel = ttk.Frame(frame_creation)
        create_right_panel.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(20, 0))

        ttk.Label(create_left_panel, text="Ajouter un article", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 15))
        ttk.Label(create_left_panel, text="Nom de l'article :", style='Sub.TLabel').pack(anchor=tk.W)
        self.entry_name = ttk.Entry(create_left_panel)
        self.entry_name.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)
        ttk.Label(create_left_panel, text="Prix (€) :", style='Sub.TLabel').pack(anchor=tk.W)
        self.entry_price = ttk.Entry(create_left_panel)
        self.entry_price.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)
        ttk.Button(create_left_panel, text="Créer l'article", command=self.handle_add_article).pack(anchor=tk.W, pady=10, fill=tk.X)

        ttk.Label(create_right_panel, text="Ajouter un utilisateur", style='Header.TLabel').pack(anchor=tk.W, pady=(0, 15))
        ttk.Label(create_right_panel, text="Nom :", style='Sub.TLabel').pack(anchor=tk.W)
        self.entry_nom = ttk.Entry(create_right_panel)
        self.entry_nom.pack(anchor=tk.W, pady=(0, 5), fill=tk.X)
        ttk.Label(create_right_panel, text="Prénom :", style='Sub.TLabel').pack(anchor=tk.W)
        self.entry_prenom = ttk.Entry(create_right_panel)
        self.entry_prenom.pack(anchor=tk.W, pady=(0, 5), fill=tk.X)
        ttk.Label(create_right_panel, text="Téléphone :", style='Sub.TLabel').pack(anchor=tk.W)
        self.entry_phone = ttk.Entry(create_right_panel)
        self.entry_phone.pack(anchor=tk.W, pady=(0, 5), fill=tk.X)
        ttk.Label(create_right_panel, text="Dépôt initial (€) :", style='Sub.TLabel').pack(anchor=tk.W)
        self.entry_solde = ttk.Entry(create_right_panel)
        self.entry_solde.pack(anchor=tk.W, pady=(0, 10), fill=tk.X)
        ttk.Button(create_right_panel, text="Créer l'utilisateur", command=self.handle_create_user).pack(anchor=tk.W, pady=10, fill=tk.X)
        
        ttk.Separator(create_right_panel, orient='horizontal').pack(fill=tk.X, pady=20)
        ttk.Button(create_right_panel, text="Importer depuis CSV", command=self.handle_import_csv).pack(anchor=tk.W, pady=10, fill=tk.X)

    def refresh_users(self):
        users = self.cbs['get_users']()
        self.all_users = [(f"{firstname} {name}", uid, firstname, name) for uid, name, firstname in users]
        self.search_bar.all_users = self.all_users
        self.search_bar.update_list(self.all_users)
        self.search_bar.set("")

    def on_user_selected(self, uid, display_name):
        total = self.cbs['get_balance'](uid)
        self.user_label.config(text=f"Utilisateur sélectionné : {display_name}")
        self.total_label.config(text=f"Solde : {total:.2f} €")

    def update_article_buttons(self):
        for widget in self.scroll_frame.winfo_children(): widget.destroy()
        articles = self.cbs['get_articles']()
        for article in articles:
            ttk.Button(self.scroll_frame, text=f"{article['name']} - {article['price']:.2f} €", style='Gold.TButton', command=lambda a=article: self.handle_confirm_purchase(a)).pack(fill=tk.X, pady=4)
    def handle_add_article(self):
        name = self.entry_name.get().strip()
        try: price = float(self.entry_price.get())
        except ValueError: messagebox.showerror("Erreur", "Le prix doit être un nombre."); return
        if messagebox.askyesno("Confirmation", f"Ajouter '{name}' pour {price} € ?"):
            self.cbs['add_article'](name, price); self.entry_name.delete(0, tk.END); self.entry_price.delete(0, tk.END); self.update_article_buttons(); messagebox.showinfo("Succès", "Article ajouté.")
    def handle_confirm_purchase(self, article):
        display_name = self.search_bar.get()
        uid = next((u[1] for u in self.all_users if u[0] == display_name), None)
        if not uid: return
        if messagebox.askyesno("Confirmation", f"Confirmer l'achat de {article['name']} ?"):
            self.cbs['add_purchase'](uid, article['name'], article['price']); self.on_user_selected(uid, display_name)
    def handle_create_user(self):
        n, f, p, s = self.entry_nom.get(), self.entry_prenom.get(), self.entry_phone.get(), self.entry_solde.get()
        try: bal = float(s)
        except ValueError: messagebox.showerror("Erreur", "Solde invalide"); return
        if not n or not f or not p: messagebox.showerror("Erreur", "Champs requis"); return
        if messagebox.askyesno("Confirmation", f"Créer l'utilisateur {f} {n} ?"):
            if self.cbs['add_user'](n, f, p, bal): self.refresh_users(); self.entry_nom.delete(0, tk.END); self.entry_prenom.delete(0, tk.END); self.entry_phone.delete(0, tk.END); self.entry_solde.delete(0, tk.END); messagebox.showinfo("Succès", "Utilisateur créé.")
    def handle_add_balance(self):
        display_name = self.search_bar.get()
        uid = next((u[1] for u in self.all_users if u[0] == display_name), None)
        if not uid: return
        try: amt = float(self.entry_balance.get())
        except: return
        
        # Demande code PIN
        pin = simpledialog.askstring("Validation", "Entrez le code PIN :", show='*')
        if pin == "456":
            self.cbs['add_balance'](amt, uid); self.entry_balance.delete(0, tk.END); self.on_user_selected(uid, self.search_bar.get()); messagebox.showinfo("Succès", "Solde mis à jour.")
        else:
            messagebox.showerror("Erreur", "Code PIN incorrect.")
    def handle_import_csv(self):
        path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if path:
            if messagebox.askyesno("Confirmation", "Importer les utilisateurs ?"):
                c = self.cbs['import_csv'](path); self.refresh_users(); messagebox.showinfo("Succès", f"{c} utilisateurs importés.")
