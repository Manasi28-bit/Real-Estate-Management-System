"""
Beginner-Friendly Real Estate Management System
"""

import tkinter as tk
from tkinter import ttk, messagebox
import mysql.connector

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import pandas as pd

# ----------------- CONFIG -----------------
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "root",
    "database": "realestate_db"
}

# ----------------- DB -----------------
def get_db_connection():
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_CONFIG['database']}")
    conn.commit()
    cursor.close()
    conn.close()
    return mysql.connector.connect(**DB_CONFIG)


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS flats (
            flat_id INT AUTO_INCREMENT PRIMARY KEY,
            location VARCHAR(100),
            area VARCHAR(50),
            price DECIMAL(10,2),
            status VARCHAR(50),
            seller_name VARCHAR(100)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS clients (
            client_id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100),
            contact VARCHAR(15),
            preferred_area VARCHAR(100),
            budget DECIMAL(10,2)
        )
    """)

    conn.commit()
    cursor.close()
    conn.close()


# ----------------- MAIN APP -----------------
class RealEstateApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Real Estate Management System")
        self.geometry("1050x650")
        self.configure(bg="white")

        header = tk.Label(
            self, text="Real Estate Management System",
            font=("Segoe UI", 20, "bold"),
            bg="#00BFFF", fg="white", pady=12
        )
        header.pack(fill="x")

        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill="both", expand=True, padx=20, pady=20)

        self.create_flats_tab()
        self.create_clients_tab()
        self.create_visual_tab()

        init_db()
        self.refresh_all()

    # ---------------- VISUAL TAB ----------------
    def create_visual_tab(self):
        frame = ttk.Frame(self.notebook, padding=40)
        self.notebook.add(frame, text="Visualizations")

        tk.Label(frame, text="Flats Availability",
                 font=("Segoe UI", 14, "bold")).pack(pady=20)

        tk.Button(
            frame, text="Show Pie Chart",
            command=self.show_pie_chart,
            bg="#00BFFF", fg="white",
            width=30, height=2
        ).pack()

    def show_pie_chart(self):
        conn = get_db_connection()
        df = pd.read_sql("SELECT status FROM flats", conn)
        conn.close()

        if df.empty:
            messagebox.showwarning("No Data", "No flats data available")
            return

        counts = df["status"].value_counts()
        plt.figure(figsize=(5, 5))
        plt.pie(counts, labels=counts.index, autopct="%1.1f%%", startangle=90)
        plt.title("Flats Availability")
        plt.show()

    # ---------------- FLATS TAB ----------------
    def create_flats_tab(self):
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="Flats")

        left = ttk.LabelFrame(frame, text="Flat Details", padding=20)
        left.pack(side="left", fill="y", padx=(0, 20))

        self.p_location = tk.Entry(left, width=28)
        self.p_area = tk.Entry(left, width=28)
        self.p_price = tk.Entry(left, width=28)
        self.p_status = ttk.Combobox(
            left, values=["Available", "Not Available"],
            state="readonly", width=26
        )
        self.p_status.current(0)
        self.p_seller = tk.Entry(left, width=28)

        fields = [
            ("Location", self.p_location),
            ("Area", self.p_area),
            ("Price", self.p_price),
            ("Status", self.p_status),
            ("Seller Name", self.p_seller)
        ]

        for i, (lbl, widget) in enumerate(fields):
            tk.Label(left, text=lbl + ":").grid(row=i, column=0, sticky="w", pady=6)
            widget.grid(row=i, column=1, pady=6)

        btn_frame = tk.Frame(left)
        btn_frame.grid(row=6, column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="Add", command=self.add_flat,
                  bg="#87CEEB", width=10).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Update", command=self.update_flat,
                  bg="#00BFFF", fg="white", width=10).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete", command=self.delete_flat,
                  bg="#FF6347", fg="white", width=10).pack(side="left", padx=4)

        right = ttk.LabelFrame(frame, text="Flats List", padding=10)
        right.pack(side="left", fill="both", expand=True)

        cols = ("ID", "Location", "Area", "Price", "Status", "Seller")
        self.tree_flats = ttk.Treeview(right, columns=cols, show="headings")

        for c in cols:
            self.tree_flats.heading(c, text=c)
            self.tree_flats.column(c, width=130, anchor="center")

        self.tree_flats.pack(fill="both", expand=True)
        self.tree_flats.bind("<<TreeviewSelect>>", self.on_flat_select)

    def add_flat(self):
        try:
            price = float(self.p_price.get())
        except ValueError:
            messagebox.showerror("Invalid", "Price must be numeric")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO flats (location, area, price, status, seller_name) VALUES (%s,%s,%s,%s,%s)",
            (self.p_location.get(), self.p_area.get(), price, self.p_status.get(), self.p_seller.get())
        )
        conn.commit()
        cursor.close()
        conn.close()
        self.refresh_flats()

    def on_flat_select(self, _):
        selected = self.tree_flats.selection()
        if selected:
            row = self.tree_flats.item(selected[0])["values"]
            self.p_location.delete(0, "end")
            self.p_location.insert(0, row[1])
            self.p_area.delete(0, "end")
            self.p_area.insert(0, row[2])
            self.p_price.delete(0, "end")
            self.p_price.insert(0, row[3])
            self.p_status.set(row[4])
            self.p_seller.delete(0, "end")
            self.p_seller.insert(0, row[5])

    def update_flat(self):
        selected = self.tree_flats.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a flat first")
            return

        flat_id = self.tree_flats.item(selected[0])["values"][0]

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE flats SET location=%s, area=%s, price=%s, status=%s, seller_name=%s
               WHERE flat_id=%s""",
            (
                self.p_location.get(),
                self.p_area.get(),
                float(self.p_price.get()),
                self.p_status.get(),
                self.p_seller.get(),
                flat_id
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        self.refresh_flats()

    def delete_flat(self):
        selected = self.tree_flats.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a flat first")
            return

        flat_id = self.tree_flats.item(selected[0])["values"][0]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM flats WHERE flat_id=%s", (flat_id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.refresh_flats()

    def refresh_flats(self):
        self.tree_flats.delete(*self.tree_flats.get_children())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM flats")
        for row in cursor.fetchall():
            self.tree_flats.insert("", "end", values=row)
        cursor.close()
        conn.close()

    # ---------------- CLIENTS TAB ----------------
    def create_clients_tab(self):
        frame = ttk.Frame(self.notebook, padding=20)
        self.notebook.add(frame, text="Clients")

        left = ttk.LabelFrame(frame, text="Client Details", padding=20)
        left.pack(side="left", fill="y", padx=(0, 20))

        self.c_name = tk.Entry(left, width=28)
        self.c_contact = tk.Entry(left, width=28)
        self.c_area = tk.Entry(left, width=28)
        self.c_budget = tk.Entry(left, width=28)

        fields = [
            ("Name", self.c_name),
            ("Contact", self.c_contact),
            ("Preferred Area", self.c_area),
            ("Budget", self.c_budget)
        ]

        for i, (lbl, widget) in enumerate(fields):
            tk.Label(left, text=lbl + ":").grid(row=i, column=0, sticky="w", pady=6)
            widget.grid(row=i, column=1, pady=6)

        btn_frame = tk.Frame(left)
        btn_frame.grid(row=5, column=0, columnspan=2, pady=15)

        tk.Button(btn_frame, text="Add", command=self.add_client,
                  bg="#87CEEB", width=10).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Update", command=self.update_client,
                  bg="#00BFFF", fg="white", width=10).pack(side="left", padx=4)
        tk.Button(btn_frame, text="Delete", command=self.delete_client,
                  bg="#FF6347", fg="white", width=10).pack(side="left", padx=4)

        right = ttk.LabelFrame(frame, text="Clients List", padding=10)
        right.pack(side="left", fill="both", expand=True)

        cols = ("ID", "Name", "Contact", "Preferred Area", "Budget")
        self.tree_clients = ttk.Treeview(right, columns=cols, show="headings")

        for c in cols:
            self.tree_clients.heading(c, text=c)
            self.tree_clients.column(c, width=140, anchor="center")

        self.tree_clients.pack(fill="both", expand=True)
        self.tree_clients.bind("<<TreeviewSelect>>", self.on_client_select)

    def add_client(self):
        try:
            budget = float(self.c_budget.get()) if self.c_budget.get() else 0
        except ValueError:
            messagebox.showerror("Invalid", "Budget must be numeric")
            return

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO clients (name, contact, preferred_area, budget) VALUES (%s,%s,%s,%s)",
            (self.c_name.get(), self.c_contact.get(), self.c_area.get(), budget)
        )
        conn.commit()
        cursor.close()
        conn.close()
        self.refresh_clients()

    def on_client_select(self, _):
        selected = self.tree_clients.selection()
        if selected:
            row = self.tree_clients.item(selected[0])["values"]
            self.c_name.delete(0, "end")
            self.c_name.insert(0, row[1])
            self.c_contact.delete(0, "end")
            self.c_contact.insert(0, row[2])
            self.c_area.delete(0, "end")
            self.c_area.insert(0, row[3])
            self.c_budget.delete(0, "end")
            self.c_budget.insert(0, row[4])

    def update_client(self):
        selected = self.tree_clients.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a client first")
            return

        client_id = self.tree_clients.item(selected[0])["values"][0]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            """UPDATE clients SET name=%s, contact=%s, preferred_area=%s, budget=%s
               WHERE client_id=%s""",
            (
                self.c_name.get(),
                self.c_contact.get(),
                self.c_area.get(),
                float(self.c_budget.get() or 0),
                client_id
            )
        )
        conn.commit()
        cursor.close()
        conn.close()
        self.refresh_clients()

    def delete_client(self):
        selected = self.tree_clients.selection()
        if not selected:
            messagebox.showwarning("Select", "Select a client first")
            return

        client_id = self.tree_clients.item(selected[0])["values"][0]
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clients WHERE client_id=%s", (client_id,))
        conn.commit()
        cursor.close()
        conn.close()
        self.refresh_clients()

    def refresh_clients(self):
        self.tree_clients.delete(*self.tree_clients.get_children())
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients")
        for row in cursor.fetchall():
            self.tree_clients.insert("", "end", values=row)
        cursor.close()
        conn.close()

    def refresh_all(self):
        self.refresh_flats()
        self.refresh_clients()


# ---------------- RUN APP ----------------
if __name__ == "__main__":
    app = RealEstateApp()
    app.mainloop()
