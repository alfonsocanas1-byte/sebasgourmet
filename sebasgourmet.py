# sebasgourmet.py
import random
import urllib.parse
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client

# Configuración de la página
st.set_page_config(
    page_title="Sebas Gourmet - Pedidos", page_icon="🍲", layout="centered"
)

# ==========================================
# CREDENCIALES DE SUPABASE
# ==========================================
SUPABASE_URL = "https://tu-proyecto-id.supabase.co"
SUPABASE_KEY = "tu-clave-anon-key-larga-aqui"

try:
  supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
  st.error(f"Error al conectar con Supabase: {e}")

# Título principal
st.title("🍲 Sebas Gourmet")
st.markdown(
    "### Sistema de Gestión de Almuerzos y Platos Especiales/Eventos"
)

# Menú disponible y precios en COP
MENU = {
    "Costilla de cerdo a la bbq más acompañantes": 22000,
    "Pollo en salsa de champiñones más acompañantes": 17000,
    "Carne de res asada más acompañantes": 17000,
    "Arroz con pollo más acompañantes": 17000,
    "Plato gourmet (Especial toda la semana - Postre frasco grande)": 150000,
}

with st.form("form_sebas_gourmet"):
  st.subheader("1. Datos del Cliente y Envío")
  nombre = st.text_input("Nombre cliente")
  telefono = st.text_input("Número celular (ej. 3128942010)")
  tipo_entrega = st.selectbox(
      "Tipo de entrega", ["Domicilio", "Para recogen en local", "Evento"]
  )

  st.subheader("2. Selección de Platos")
  cantidades = {}
  for plato, precio in MENU.items():
    cantidades[plato] = st.number_input(
        f"{plato} — ${precio:,.0f}", min_value=0, max_value=50, value=0, step=1
    )

  submitted = st.form_submit_button("Confirmar Pedido")

if submitted:
  if not nombre or not telefono:
    st.warning("Por favor completa el nombre y el número celular del cliente.")
  else:
    # 1. Filtrar platos seleccionados (cantidad > 0)
    platos_seleccionados = []
    for plato, cant in cantidades.items():
      if cant > 0:
        platos_seleccionados.append(
            {
                "nombre plato": plato,
                "precio_plato": MENU[plato],
                "cantidad": cant,
                "total por plato": cant * MENU[plato],
            }
        )

    if not platos_seleccionados:
      st.warning("Debes seleccionar al menos un plato para realizar el pedido.")
    else:
      # Generar un número de pedido único aleatorio
      numero_pedido = random.randint(10000, 99999)

      # Cálculos generales
      total_platos_variedad = len(platos_seleccionados)
      total_pedido_general = sum(
          item["total por plato"] for item in platos_seleccionados
      )

      # 2. Insertar cada plato como una fila en la tabla exacta de Supabase
      try:
        registros_a_insertar = []
        for item in platos_seleccionados:
          fila = {
              "número pedido": numero_pedido,
              "nombre cliente": nombre,
              "número celular": int(telefono),
              "tipo de entrega": tipo_entrega,
              "nombre plato": item["nombre plato"],
              "precio_plato": item["precio_plato"],
              "cantidad": item["cantidad"],
              "total por plato": item["total por plato"],
              "total platos": total_platos_variedad,
              "total pedido": total_pedido_general,
          }
          registros_a_insertar.append(fila)

        # Nombre exacto de la tabla tal como aparece en tu panel de Supabase:
        supabase.table("Pedidosebasgourmet").insert(
            registros_a_insertar
        ).execute()
        st.success(
            "¡Pedido registrado exitosamente en la base de datos con el N°"
            f" {numero_pedido}!"
        )
      except Exception as e:
        st.error(f"Error al guardar en la base de datos de Supabase: {e}")

      # 3. Construir mensaje detallado para WhatsApp (Número: 3128942010)
      whatsapp_numero = "573128942010"
      mensaje_wa = (
          f"¡Hola Sebas Gourmet! 🍽️ Nuevo Pedido N° {numero_pedido}:\n\n"
          f"👤 *Cliente:* {nombre}\n"
          f"📞 *Celular:* {telefono}\n"
          f"📦 *Tipo de entrega:* {tipo_entrega}\n\n"
          f"🛒 *Detalle de platos:*\n"
      )

      for item in platos_seleccionados:
        mensaje_wa += (
            f"- {item['cantidad']}x {item['nombre plato']} | Subtotal:"
            f" ${item['total por plato']:,.0f}\n"
        )

      mensaje_wa += (
          f"\n💰 *Total General del Pedido:* ${total_pedido_general:,.0f}"
      )

      mensaje_encoded = urllib.parse.quote(mensaje_wa)
      whatsapp_url = f"https://wa.me/{whatsapp_numero}?text={mensaje_encoded}"

      st.markdown("---")
      st.subheader("3. Enviar a WhatsApp")
      st.markdown(
          "Haz clic en el botón para enviar el comprobante y detalle del"
          f" pedido al WhatsApp del restaurante: [📲 Enviar Pedido por"
          f" WhatsApp]({whatsapp_url})"
      )