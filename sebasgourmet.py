import json
import os
from datetime import datetime

DB_FILE = "pedidossebasgourmet.json"
KEY_ACCESO = "5050"

def cargar_datos():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_datos(pedidos):
    with open(DB_FILE, "w") as f:
        json.dump(pedidos, f, indent=4)

def nuevo_pedido():
    print("\n--- NUEVO PEDIDO ---")
    nombre = input("Nombre responsable: ")
    celular = input("Número de celular: ")
    
    print("1. Menú del día ($12.000)")
    print("2. Particular ($20.000)")
    tipo = input("Seleccione tipo (1/2): ")
    
    detalle_particular = ""
    if tipo == "2":
        detalle_particular = input("Redacción del pedido particular: ")
        precio_unitario = 20000
    else:
        precio_unitario = 12000

    cantidad = int(input("Cantidad de menús: "))
    fecha_entrega = input("Fecha y hora de entrega (Ej: 2026-03-17 14:00): ")
    
    pedido = {
        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
        "nombre": nombre,
        "celular": celular,
        "tipo": "Menu del dia" if tipo == "1" else "Particular",
        "detalle": detalle_particular,
        "cantidad": cantidad,
        "total": cantidad * precio_unitario,
        "fecha_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "fecha_entrega": fecha_entrega,
        "notas": "",
        "estado": "🔴"  # Semáforo inicial
    }
    
    pedidos = cargar_datos()
    pedidos.append(pedido)
    guardar_datos(pedidos)
    print("✔ Pedido guardado con éxito.")

def gestionar_pedidos():
    while True:
        pedidos = cargar_datos()
        print("\n--- GESTIÓN DE PEDIDOS ---")
        for i, p in enumerate(pedidos):
            print(f"{i}. [{p['estado']}] {p['nombre']} - Entrega: {p['fecha_entrega']}")
        
        print("\nOpciones: [ID del pedido] para editar / 's' para salir")
        opcion = input("> ")
        
        if opcion.lower() == 's': break
        
        try:
            idx = int(opcion)
            p = pedidos[idx]
            print(f"\nEditando pedido de {p['nombre']}")
            print(f"Notas actuales: {p['notas']}")
            p['notas'] = input("Nueva nota (o enter para mantener): ") or p['notas']
            
            print("Estados: 🔴 (Pendiente), 🟡 (En proceso), 🟢 (Entregado)")
            p['estado'] = input("Cambiar semáforo (icono o color): ") or p['estado']
            
            guardar_datos(pedidos)
            print("✔ Cambios guardados.")
        except:
            print("Opción no válida.")

def main():
    llave = input("Ingrese la llave de acceso: ")
    if llave != KEY_ACCESO:
        print("Acceso denegado.")
        return

    while True:
        print("\n--- SEBASGOURMET ---")
        print("1. Crear Pedido")
        print("2. Ver/Editar Pedidos")
        print("3. Salir")
        op = input("> ")
        
        if op == "1": nuevo_pedido()
        elif op == "2": gestionar_pedidos()
        elif op == "3": break

if __name__ == "__main__":
    main()