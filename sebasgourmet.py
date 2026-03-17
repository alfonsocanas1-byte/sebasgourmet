import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "pedidossebasgourmet.json"
KEY_ACCESO = "5050"

# Configuración de página
st.set_page_config(page_title="Sebasgourmet", page_icon="🍲")

def cargar_datos():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)
    with open(DB_FILE, "r") as f:
        return json.load(f)

def guardar_datos(pedidos):
    with open(DB_FILE, "w") as f:
        json.dump(pedidos, f, indent=4)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    col1, col2 = st.columns([1, 2])
    llave = st.text_input("Llave de acceso:", type="password")
    if st.button("Ingresar"):
        if llave == KEY_ACCESO:
            st.session_state.autenticado = True
            st.rerun()
        else:
            st.error("Llave incorrecta")
    st.stop()

# --- APP PRINCIPAL ---
st.title("🍲 Sebasgourmet")
menu = st.sidebar.selectbox("Menú", ["Nuevo Pedido", "Gestionar Pedidos"])

pedidos = cargar_datos()

if menu == "Nuevo Pedido":
    st.subheader("📝 Crear Pedido")
    
    with st.form("form_pedido", clear_on_submit=True):
        nombre = st.text_input("Nombre responsable")
        celular = st.text_input("Número de celular")
        tipo = st.radio("Tipo de menú", ["Menú del día ($12.000)", "Particular ($20.000)"])
        
        detalle_particular = ""
        precio_unitario = 12000
        if "Particular" in tipo:
            detalle_particular = st.text_area("Redacción del pedido particular")
            precio_unitario = 20000
            
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
        fecha_entrega = st.text_input("Fecha y hora de entrega", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        enviar = st.form_submit_button("Guardar Pedido")
        
        if enviar:
            nuevo = {
                "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                "nombre": nombre,
                "celular": celular,
                "tipo": "Menú del día" if precio_unitario == 12000 else "Particular",
                "detalle": detalle_particular,
                "cantidad": cantidad,
                "total": cantidad * precio_unitario,
                "fecha_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "fecha_entrega": fecha_entrega,
                "notas": "",
                "estado": "🔴"
            }
            pedidos.append(nuevo)
            guardar_datos(pedidos)
            st.success("✔ Pedido guardado")

elif menu == "Gestionar Pedidos":
    st.subheader("📋 Pedidos Activos")
    
    if not pedidos:
        st.info("No hay pedidos registrados.")
    else:
        for i, p in enumerate(pedidos):
            with st.expander(f"{p['estado']} {p['nombre']} - {p['fecha_entrega']}"):
                st.write(f"**Tipo:** {p['tipo']} | **Cantidad:** {p['cantidad']}")
                st.write(f"**Total:** ${p['total']:,} COP")
                if p['detalle']: st.write(f"**Detalle:** {p['detalle']}")
                
                # Edición constante
                nueva_nota = st.text_area("Notas / Cuadro de diálogo", value=p['notas'], key=f"nota_{i}")
                nuevo_estado = st.selectbox("Estado (Semáforo)", ["🔴", "🟡", "🟢"], 
                                           index=["🔴", "🟡", "🟢"].index(p['estado']), key=f"est_{i}")
                
                if st.button("Actualizar", key=f"btn_{i}"):
                    pedidos[i]['notas'] = nueva_nota
                    pedidos[i]['estado'] = nuevo_estado
                    guardar_datos(pedidos)
                    st.success("Cambios guardados")
                    st.rerun()