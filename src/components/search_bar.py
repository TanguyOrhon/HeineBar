import tkinter as tk
from tkinter import ttk

class UserSearchBar(ttk.Frame):
    def __init__(self, parent, users_data, callback_selected, **kwargs):
        super().__init__(parent)
        self.all_users = users_data 
        self.callback_selected = callback_selected
        
        self.entry = ttk.Entry(self, **kwargs)
        self.entry.pack(fill=tk.X)
        self.entry.bind("<KeyRelease>", self.on_key_release)
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)
        
        self.listbox = tk.Listbox(self, height=5, bg="#1e1e1e", fg="#ffffff", selectbackground="#008226", borderwidth=0, highlightthickness=0)
        self.listbox.bind("<<ListboxSelect>>", self.on_selected)
        
        # Astuce pour masquer le listbox quand on clique ailleurs
        self.listbox.bind("<FocusOut>", self.on_focus_out)

    def update_list(self, user_list):
        self.listbox.delete(0, tk.END)
        for item in user_list:
            self.listbox.insert(tk.END, item[0])
        
        if user_list and self.entry.get():
            self.listbox.pack(fill=tk.X)
        else:
            self.listbox.pack_forget()

    def on_key_release(self, event):
        typed = self.entry.get().lower()
        filtered = [u for u in self.all_users if typed in u[0].lower() or typed in u[2].lower() or typed in u[3].lower()]
        self.update_list(filtered)

    def on_focus_in(self, event):
        if self.entry.get():
            self.listbox.pack(fill=tk.X)

    def on_focus_out(self, event):
        # Utiliser after pour laisser le temps au clic de se produire dans le listbox avant de masquer
        self.after(200, self.check_focus_out)

    def check_focus_out(self):
        try:
            focus = self.focus_get()
            if focus != self.listbox and focus != self.entry:
                self.listbox.pack_forget()
        except KeyError:
            # Handle cases where focus_get() returns a widget that is being destroyed
            pass

    def on_selected(self, event=None):
        selection = self.listbox.curselection()
        if selection:
            display_name = self.listbox.get(selection[0])
            self.entry.delete(0, tk.END)
            self.entry.insert(0, display_name)
            self.listbox.pack_forget()
            for name, uid, _, _ in self.all_users:
                if name == display_name:
                    self.callback_selected(uid, name)
                    break

    def get(self):
        return self.entry.get()

    def set(self, text):
        self.entry.delete(0, tk.END)
        self.entry.insert(0, text)
