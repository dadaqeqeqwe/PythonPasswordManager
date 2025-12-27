import os
import json
import random
import string
import customtkinter as ctk
from tkinter import messagebox
from cryptography.fernet import Fernet
from PIL import Image

DATA_DIR = "data"
KEY_FILE = os.path.join(DATA_DIR, "secret.key")
DATA_FILE = os.path.join(DATA_DIR, "passwords.json")

os.makedirs(DATA_DIR, exist_ok=True)

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

cipher = Fernet(load_key())

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(length))

def load_passwords():
    if not os.path.exists(DATA_FILE):
        return {}

    with open(DATA_FILE, "r") as f:
        data = json.load(f)

    result = {}
    for site, info in data.items():
        pwd = cipher.decrypt(info["password"].encode()).decode()
        result[site] = (info["email"], pwd)
    return result

def save_password(site, email, password):
    data = {}

    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            data = json.load(f)

    encrypted = cipher.encrypt(password.encode()).decode()
    data[site] = {"email": email, "password": encrypted}

    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

app = ctk.CTk()
app.title("Password Manager")
app.geometry("600x600")
app.resizable(False, False)

logo = ctk.CTkImage(
    Image.open("img/logo.png"),
    size=(200, 200)
)

ctk.CTkLabel(app, image=logo, text="").pack(pady=20)

site_entry = ctk.CTkEntry(app, width=400, placeholder_text="Website")
site_entry.pack(pady=10)

email_entry = ctk.CTkEntry(app, width=400, placeholder_text="Email / Login")
email_entry.pack(pady=10)

password_entry = ctk.CTkEntry(app, width=400, placeholder_text="Password")
password_entry.pack(pady=10)

def gen_pass():
    password_entry.delete(0, "end")
    password_entry.insert(0, generate_password())

def save():
    s = site_entry.get()
    e = email_entry.get()
    p = password_entry.get()

    if not s or not e or not p:
        messagebox.showerror("Error", "Fill all fields")
        return

    save_password(s, e, p)
    messagebox.showinfo("Saved", "Password saved")
    site_entry.delete(0, "end")
    email_entry.delete(0, "end")
    password_entry.delete(0, "end")
    refresh()

ctk.CTkButton(app, text="Generate password", command=gen_pass).pack(pady=5)
ctk.CTkButton(app, text="Save password", command=save).pack(pady=5)

box = ctk.CTkTextbox(app, width=520, height=200)
box.pack(pady=20)

def refresh():
    box.delete("1.0", "end")
    data = load_passwords()
    for site, (email, pwd) in data.items():
        box.insert("end", f"{site} | {email} | {pwd}\n")

refresh()

app.mainloop()

