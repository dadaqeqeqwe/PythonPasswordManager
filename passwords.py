import tkinter as tk
from tkinter import messagebox
import random
import string
import os
from cryptography.fernet import Fernet

KEY_FILE = "secret.key"
DATA_FILE = "passwords.dat"

def load_key():
    if not os.path.exists(KEY_FILE):
        key = Fernet.generate_key()
        with open(KEY_FILE, "wb") as f:
            f.write(key)
    else:
        with open(KEY_FILE, "rb") as f:
            key = f.read()
    return key

key = load_key()
cipher = Fernet(key)

def generate_password(length=16):
    chars = string.ascii_letters + string.digits + string.punctuation
    return "".join(random.choice(chars) for _ in range(length))

def save_password():
    service = service_entry.get()
    login = login_entry.get()
    password = password_entry.get()

    if not service or not login or not password:
        messagebox.showerror("Ошибка", "Заполните все поля")
        return

    record = f"{service} | {login} | {password}"
    encrypted = cipher.encrypt(record.encode())

    with open(DATA_FILE, "ab") as f:
        f.write(encrypted + b"\n")

    messagebox.showinfo("Готово", "Пароль сохранён")
    clear_fields()

def load_passwords():
    output.delete(1.0, tk.END)

    if not os.path.exists(DATA_FILE):
        return

    with open(DATA_FILE, "rb") as f:
        for line in f:
            decrypted = cipher.decrypt(line.strip()).decode()
            output.insert(tk.END, decrypted + "\n")

def generate_and_insert():
    password_entry.delete(0, tk.END)
    password_entry.insert(0, generate_password())

def clear_fields():
    service_entry.delete(0, tk.END)
    login_entry.delete(0, tk.END)
    password_entry.delete(0, tk.END)

root = tk.Tk()
root.title("Менеджер паролей")
root.geometry("500x500")

tk.Label(root, text="Сервис").pack()
service_entry = tk.Entry(root, width=40)
service_entry.pack()

tk.Label(root, text="Логин").pack()
login_entry = tk.Entry(root, width=40)
login_entry.pack()

tk.Label(root, text="Пароль").pack()
password_entry = tk.Entry(root, width=40)
password_entry.pack()

tk.Button(root, text="Сгенерировать пароль", command=generate_and_insert).pack(pady=5)
tk.Button(root, text="Сохранить пароль", command=save_password).pack(pady=5)
tk.Button(root, text="Показать сохранённые пароли", command=load_passwords).pack(pady=5)

output = tk.Text(root, height=10, width=60)
output.pack(pady=10)

root.mainloop()