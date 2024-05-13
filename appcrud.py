import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from tkcalendar import DateEntry

class CitaDB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS citas (
                id INTEGER PRIMARY KEY,
                nombre_cliente TEXT,
                servicio TEXT,
                fecha DATE,
                hora TIME,
                estado TEXT
            )
        """)
        self.conn.commit()

    def execute_query(self, query, *args):
        try:
            self.cursor.execute(query, args)
            self.conn.commit()
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Error de base de datos", str(e))

    def fetch_all_citas(self):
        return self.execute_query("SELECT * FROM citas")

class CitasCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestión de Citas")
        self.db = CitaDB("citas.db")

        self.create_widgets()
        self.load_citas() 

    def create_widgets(self):
        self.create_treeview()
        self.create_input_fields()
        self.create_buttons()
        self.create_scrollbars()

    def create_treeview(self):
        self.tree = ttk.Treeview(self.root, columns=("ID", "Nombre del Cliente", "Servicio", "Fecha", "Hora" , "Estado"), show="headings")
        self.tree.heading("ID", text="ID")
        self.tree.heading("Nombre del Cliente", text="Nombre del Cliente")
        self.tree.heading("Servicio", text="Servicio")
        self.tree.heading("Fecha", text="Fecha")
        self.tree.heading("Hora", text="Hora")
        self.tree.heading("Estado", text="Estado")
        self.tree.grid(row=0, column=0, sticky="nsew")
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def create_input_fields(self):
        fields = [("Nombre del Cliente:", 30), ("Servicio:", 10),("Fecha:", 10), ("Hora:", 10), ("Estado:", 10)]
        input_frame = ttk.Frame(self.root)
        input_frame.grid(row=1, column=0, pady=5)

        self.entries = {}
        for i, (label_text, width) in enumerate(fields):
            label = ttk.Label(input_frame, text=label_text)
            label.grid(row=i, column=0, pady=(0, 5), padx=10, sticky="w")

            if label_text == "Fecha:":
                # Agregar un campo de entrada de fecha con calendario
                date_entry = DateEntry(input_frame, width=width, date_pattern='dd/mm/yyyy')
                date_entry.grid(row=i, column=1, pady=(0, 10), padx=10, sticky="ew")
                self.entries[label_text] = date_entry
            elif label_text == "Servicio:":
                # Crear un Combobox para el campo Servicio
                combobox = ttk.Combobox(input_frame, values=["Manicura", "Pedicura"], width=width)
                combobox.grid(row=i, column=1, pady=(0, 10), padx=10, sticky="ew")
                self.entries[label_text] = combobox
            elif label_text == "Hora:":
                # Crear un Combobox para el campo Hora
                combobox = ttk.Combobox(input_frame, values=["9:00 am", "10:00 am", "11:00 am", "2:00 pm", "3:00 pm", "4:00 pm", "5:00 pm", "6:00 pm", "7:00 pm"], width=width)
                combobox.grid(row=i, column=1, pady=(0, 10), padx=10, sticky="ew")
                self.entries[label_text] = combobox
            elif label_text == "Estado:":
                # Crear un Combobox para el campo Estado
                combobox = ttk.Combobox(input_frame, values=["Confirmada", "Pendiente", "Cancelada"], width=width)
                combobox.grid(row=i, column=1, pady=(0, 10), padx=10, sticky="ew")
                self.entries[label_text] = combobox
            else:
                entry = ttk.Entry(input_frame, width=width)
                entry.grid(row=i, column=1, pady=(0, 10), padx=10, sticky="ew")
                self.entries[label_text] = entry

    def create_buttons(self):
        btn_frame = ttk.Frame(self.root)
        btn_frame.grid(row=2, column=0, pady=(0, 10))

        buttons = [("Agendar Cita", self.add_citas), 
                   ("Eliminar", self.remove_citas),
                   ("Actualizar", self.update_citas), 
                   ("Buscar", self.search_citas),
                   ("Todas las Citas", self.show_all_citas)]

        for text, command in buttons:
            button = ttk.Button(btn_frame, text=text, command=command)
            button.grid(row=0, column=buttons.index((text, command)), padx=5)

    def create_scrollbars(self):
        # Crear una barra de desplazamiento vertical
        yscrollbar = ttk.Scrollbar(self.root, orient="vertical", command=self.tree.yview)
        yscrollbar.grid(row=0, column=1, sticky="ns")
        self.tree.configure(yscrollcommand=yscrollbar.set)

    def load_citas(self):
        self.clear_table()
        for row in self.db.fetch_all_citas():
            self.tree.insert("", "end", values=row)

    def add_citas(self):
        values = [entry.get() for entry in self.entries.values()]
        if all(values):
            self.db.execute_query("INSERT INTO citas (nombre_cliente, servicio, fecha, hora, estado) VALUES (?, ?, ?, ?, ?)", *values)
            messagebox.showinfo("Éxito", "Cita agendada con éxito")
            self.load_citas()
            self.clear_input_fields()
        else:
            messagebox.showerror("Error", "Por favor, complete todos los campos")

    def remove_citas(self):
        selected_item = self.tree.selection()
        if selected_item:
            citas_id = self.tree.item(selected_item, "values")[0]
            self.db.execute_query("DELETE FROM citas WHERE id=?", citas_id)
            messagebox.showinfo("Éxito", "Cita eliminada con éxito")
            self.load_citas()
            self.clear_input_fields()
        else:
            messagebox.showerror("Error", "No se ha seleccionado ninguna cita para eliminar")

    def update_citas(self):
        selected_item = self.tree.selection()
        if selected_item:
            citas_id = self.tree.item(selected_item, "values")[0]
            values = [entry.get() for entry in self.entries.values()]
            self.db.execute_query("UPDATE citas SET nombre_cliente=?, servicio=?, fecha=?, hora=?, estado=? WHERE id=?", *(values + [citas_id]))
            messagebox.showinfo("Éxito", "Cita actualizada con éxito")
            self.load_citas()
            self.clear_input_fields()   

        else:
            messagebox.showerror("Error", "No se ha seleccionado ninguna cita para actualizar")

    def search_citas(self):
        search_term = self.entries["Nombre del Cliente:"].get()
        if search_term:
            self.clear_table()
            for row in self.db.execute_query("SELECT * FROM citas WHERE nombre_cliente LIKE ?", '%' + search_term + '%'):
                self.tree.insert("", "end", values=row)
        else:
            messagebox.showerror("Error", "Por favor, ingrese un término de búsqueda")

    def show_all_citas(self):
        self.load_citas()

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            values = self.tree.item(selected_item, "values")
            if values:
                for entry, value in zip(self.entries.values(), values[1:]):
                    entry.delete(0, tk.END)
                    entry.insert(0, value)

    def clear_input_fields(self):
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def clear_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

if __name__ == "__main__":
    root = tk.Tk()
    app = CitasCRUDApp(root)
    root.mainloop()