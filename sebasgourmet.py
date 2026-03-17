import streamlit as st
import json
import os
from datetime import datetime

DB_FILE = "pedidossebasgourmet.json"
KEY_ACCESO = "5050"

# Configuración de página
st.set_page_config(page_title="Sebasgourmet", page_icon="🍲", layout="wide")

def cargar_datos():
    if not os.path.exists(DB_FILE):
        with open(DB_FILE, "w") as f:
            json.dump([], f)
    with open(DB_FILE, "r") as f:
        try:
            return json.load(f)
        except:
            return []

def guardar_datos(pedidos):
    with open(DB_FILE, "w") as f:
        json.dump(pedidos, f, indent=4)

# --- LOGIN ---
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False

if not st.session_state.autenticado:
    st.title("🔐 Acceso")
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

# Inicializar carrito en la sesión si no existe
if "carrito" not in st.session_state:
    st.session_state.carrito = []

pedidos = cargar_datos()

if menu == "Nuevo Pedido":
    st.subheader("🛒 Carrito de Pedido")
    
    # Datos del responsable
    col_a, col_b = st.columns(2)
    with col_a:
        nombre = st.text_input("Nombre responsable")
    with col_b:
        celular = st.text_input("Número de celular")

    st.divider()

    # Interfaz de agregar al carrito
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        item_tipo = st.selectbox("Producto", ["Menú del día ($12.000)", "Particular ($20.000)"])
    with col2:
        item_cant = st.number_input("Cantidad", min_value=1, value=1)
    with col3:
        st.write(" ")
        if st.button("➕ Agregar"):
            precio = 12000 if "día" in item_tipo else 20000
            detalle = ""
            if precio == 20000:
                detalle = st.session_state.get("temp_detalle", "Sin detalle")
            
            st.session_state.carrito.append({
                "producto": item_tipo,
                "cantidad": item_cant,
                "precio": precio,
                "subtotal": precio * item_cant,
                "detalle": detalle if precio == 20000 else ""
            })

    if "Particular" in item_tipo:
        st.session_state.temp_detalle = st.text_area("Redacción del pedido particular:", key="particular_area")

    # Mostrar Carrito Actual
    if st.session_state.carrito:
        st.write("---")
        total_pedido = 0
        for i, item in enumerate(st.session_state.carrito):
            col_c1, col_c2, col_c3 = st.columns([3, 1, 1])
            with col_c1:
                st.write(f"**{item['producto']}** x{item['cantidad']} {f'({item.get('detalle', '')})' if item['detalle'] else ''}")
            with col_c2:
                st.write(f"${item['subtotal']:,}")
            with col_c3:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.carrito.pop(i)
                    st.rerun()
            total_pedido += item['subtotal']
        
        st.write(f"### Total: ${total_pedido:,} COP")
        
        fecha_entrega = st.text_input("Fecha y hora de entrega", value=datetime.now().strftime("%Y-%m-%d %H:%M"))
        
        if st.button("✅ GUARDAR PEDIDO COMPLETO"):
            if not nombre or not celular:
                st.error("Por favor ingresa nombre y celular.")
            else:
                nuevo_registro = {
                    "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                    "nombre": nombre,
                    "celular": celular,
                    "items": st.session_state.carrito,
                    "total": total_pedido,
                    "fecha_pedido": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "fecha_entrega": fecha_entrega,
                    "notas": "",
                    "estado": "🔴 Recibido"
                }
                pedidos.append(nuevo_registro)
                guardar_datos(pedidos)
                st.session_state.carrito = []
                st.success("✔ Pedido guardado con éxito")
                st.rerun()

elif menu == "Gestionar Pedidos":
    st.subheader("📋 Gestión de Pedidos")
    
    estados_semaforo = {
        "🔴 Recibido": "🔴",
        "🟠 En preparación": "🟠",
        "🟢 En camino": "🟢",
        "🔵 Entregado": "🔵"
    }

    if not pedidos:
        st.info("No hay pedidos registrados.")
    else:
        # Mostrar invertido para ver los más nuevos primero
        for i, p in enumerate(reversed(pedidos)):
            idx_real = len(pedidos) - 1 - i
            
            with st.expander(f"{p['estado']} | {p['nombre']} | Entrega: {p['fecha_entrega']}"):
                st.write(f"**📅 Realizado:** {p['fecha_pedido']}")
                st.write(f"**🚚 Entrega:** {p['fecha_entrega']}")
                st.write(f"**📞 Celular:** {p['celular']}")
                
                st.write("**Detalle del Carrito:**")
                for item in p['items']:
                    st.write(f"- {item['producto']} x{item['cantidad']} (${item['subtotal']:,}) {f'[{item['detalle']}]' if item['detalle'] else ''}")
                
                st.write(f"### Total: ${p['total']:,} COP")

                # Edición constante
                nueva_nota = st.text_area("Cuadro de diálogo (Editable)", value=p['notas'], key=f"nota_{idx_real}")
                
                # Selector de semáforo
                lista_estados = list(estados_semaforo.keys())
                estado_actual_idx = lista_estados.index(p['estado']) if p['estado'] in lista_estados else 0
                nuevo_estado = st.selectbox("Estado del pedido", lista_estados, index=estado_actual_idx, key=f"est_{idx_real}")
                
                if st.button("Guardar Cambios", key=f"btn_{idx_real}"):
                    pedidos[idx_real]['notas'] = nueva_nota
                    pedidos[index_real]['estado'] = nuevo_estado
                    guardar_datos(pedidos)
                    st.toast("Cambios guardados", icon="💾")
                    st.rerun()