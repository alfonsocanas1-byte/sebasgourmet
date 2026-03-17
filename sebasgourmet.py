import json
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime

# --- CONFIGURACIÓN DE DATOS ---
ARCHIVO_PEDIDOS = "pedidossebasgourmet.json"
LLAVE_ACCESO = "5050"

class SebasGourmetApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sebas Gourmet - Sistema de Pedidos")
        self.root.geometry("600x700")
        
        # Variables de inicio
        self.pedidos = self.cargar_datos()
        self.login_screen()

    def cargar_datos(self):
        try:
            with open(ARCHIVO_PEDIDOS, "r") as f:
                return json.load(f)
        except:
            return []

    def guardar_datos(self):
        with open(ARCHIVO_PEDIDOS, "w") as f:
            json.dump(self.pedidos, f, indent=4)

    def login_screen(self):
        self.frame_login = tk.Frame(self.root)
        self.frame_login.pack(expand=True)
        
        tk.Label(self.frame_login, text="INGRESE LLAVE SOBERANA", font=("Arial", 12, "bold")).pack(pady=10)
        self.entry_llave = tk.Entry(self.frame_login, show="*", justify="center", font=("Arial", 14))
        self.entry_llave.pack(pady=5)
        
        tk.Button(self.frame_login, text="ENTRAR", command=self.verificar_llave, bg="black", fg="white").pack(pady=20)

    def verificar_llave(self):
        if self.entry_llave.get() == LLAVE_ACCESO:
            self.frame_login.destroy()
            self.main_interface()
        else:
            messagebox.showerror("Error", "Llave Incoherente")

    def main_interface(self):
        # Contenedor Principal
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Datos del Responsable
        tk.Label(self.main_frame, text="NOMBRE RESPONSABLE:").pack(anchor="w")
        self.entry_nombre = tk.Entry(self.main_frame)
        self.entry_nombre.pack(fill="x", pady=2)

        tk.Label(self.main_frame, text="CELULAR:").pack(anchor="w")
        self.entry_celular = tk.Entry(self.main_frame)
        self.entry_celular.pack(fill="x", pady=2)

        # Opciones de Pedido
        tk.Label(self.main_frame, text="TIPO DE MENÚ:", font=("Arial", 10, "bold")).pack(pady=5)
        self.tipo_menu = tk.StringVar(value="Dia")
        tk.Radiobutton(self.main_frame, text="Menú del Día ($12.000)", variable=self.tipo_menu, value="Dia").pack(anchor="w")
        tk.Radiobutton(self.main_frame, text="Particular ($20.000)", variable=self.tipo_menu, value="Particular").pack(anchor="w")

        tk.Label(self.main_frame, text="CANTIDAD:").pack(anchor="w")
        self.spin_cantidad = tk.Spinbox(self.main_frame, from_=1, to=100)
        self.spin_cantidad.pack(fill="x")

        # Redacción para Pedido Particular
        tk.Label(self.main_frame, text="DETALLES / PARTICULAR:").pack(anchor="w")
        self.txt_particular = tk.Text(self.main_frame, height=3)
        self.txt_particular.pack(fill="x", pady=5)

        # Fecha de Entrega
        tk.Label(self.main_frame, text="FECHA/HORA ENTREGA (Ej: 2026-03-18 13:00):").pack(anchor="w")
        self.entry_entrega = tk.Entry(self.main_frame)
        self.entry_entrega.insert(0, datetime.now().strftime("%Y-%m-%d %H:%M"))
        self.entry_entrega.pack(fill="x")

        # Cuadro de Diálogo Constante (Editable y Guardar)
        tk.Label(self.main_frame, text="NOTAS DEL PEDIDO (Diálogo Constante):", fg="blue").pack(anchor="w", pady=(10,0))
        self.txt_dialogo = tk.Text(self.main_frame, height=4)
        self.txt_dialogo.pack(fill="x")

        # Semáforo de Estado
        tk.Label(self.main_frame, text="ESTADO (SEMÁFORO):").pack(anchor="w")
        self.combo_estado = ttk.Combobox(self.main_frame, values=["🔴 Pendiente", "🟡 En Preparación", "🟢 Entregado"])
        self.combo_estado.set("🔴 Pendiente")
        self.combo_estado.pack(fill="x")

        # Botones de Acción
        btn_frame = tk.Frame(self.main_frame)
        btn_frame.pack(pady=20)
        
        tk.Button(btn_frame, text="GUARDAR AVANCE", command=self.guardar_pedido, bg="gray", fg="white", width=15).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="FINALIZAR PEDIDO", command=self.guardar_pedido, bg="green", fg="white", width=15).grid(row=0, column=1, padx=5)

    def guardar_pedido(self):
        precio = 12000 if self.tipo_menu.get() == "Dia" else 20000
        total = precio * int(self.spin_cantidad.get())
        
        nuevo_pedido = {
            "id": len(self.pedidos) + 1,
            "responsable": self.entry_nombre.get(),
            "celular": self.entry_celular.get(),
            "tipo": self.tipo_menu.get(),
            "cantidad": self.spin_cantidad.get(),
            "detalles_particular": self.txt_particular.get("1.0", "end-1c"),
            "fecha_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "fecha_entrega_solicitada": self.entry_entrega.get(),
            "notas_dialogo": self.txt_dialogo.get("1.0", "end-1c"),
            "estado": self.combo_estado.get(),
            "total_cobro": total
        }
        
        self.pedidos.append(nuevo_pedido)
        self.guardar_datos()
        messagebox.showinfo("Hecho", f"Pedido Guardado. Total: ${total}")

if __name__ == "__main__":
    root = tk.Tk()
    app = SebasGourmetApp(root)
    root.mainloop()