# sebasgourmet.py
import urllib.parse
from datetime import datetime
import pandas as pd
import streamlit as st
from supabase import create_client

# Configuración de la página
st.set_page_config(
    page_title="Sebas Gourmet - Pedidos", page_icon="🍲", layout="centered"
)

# Configuración de Supabase (Lee desde st.secrets o usa valores por defecto)
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "TU_SUPABASE_URL")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "TU_SUPABASE_ANON_KEY")

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
  st.subheader("1. Datos del Cliente")
  nombre = st.text_input("Nombre completo")
  telefono = st.text_input("Número de teléfono / Celular")
  direccion = st.text_input("Dirección de entrega")

  st.subheader("2. Selección de Platos")
  cantidades = {}
  for plato, precio in MENU.items():
    cantidades[plato] = st.number_input(
        f"{plato} — ${precio:,.0f}", min_value=0, max_value=50, value=0, step=1
    )

  submitted = st.form_submit_button("Confirmar Pedido")

if submitted:
  if not nombre or not telefono or not direccion:
    st.warning(
        "Por favor completa el nombre, el teléfono y la dirección de entrega."
    )
  else:
    resumen_items = []
    total_pagar = 0

    for plato, cantidad in cantidades.items():
      if cantidad > 0:
        subtotal = cantidad * MENU[plato]
        total_pagar += subtotal
        resumen_items.append(f"{cantidad}x {plato} (${subtotal:,.0f})")

    if total_pagar == 0:
      st.warning("Debes seleccionar al menos un plato para realizar el pedido.")
    else:
      detalle_texto = " | ".join(resumen_items)

      # 1. Guardar en Supabase (Tabla: pedidos)
      try:
        data = {
            "nombre_cliente": nombre,
            "telefono_cliente": telefono,
            "direccion": direccion,
            "detalle_pedido": detalle_texto,
            "total": total_pagar,
            "estado": "Pendiente",
        }
        supabase.table("pedidos").insert(data).execute()
        st.success("¡Pedido registrado exitosamente en la base de datos!")
      except Exception as e:
        st.error(
            "Error al guardar en la base de datos (verifica tus credenciales de"
            f" Supabase): {e}"
        )

      # 2. Generar enlace de WhatsApp (Número: 3128942010)
      whatsapp_numero = "573128942010"
      mensaje_wa = (
          f"¡Hola Sebas Gourmet! 🍽️ Tengo un nuevo pedido:\n\n"
          f"👤 *Cliente:* {nombre}\n"
          f"📞 *Teléfono:* {telefono}\n"
          f"📍 *Dirección:* {direccion}\n\n"
          f"🛒 *Detalle del pedido:*\n"
      )
      for item in resumen_items:
        mensaje_wa += f"- {item}\n"
      mensaje_wa += f"\n💰 *Total a pagar:* ${total_pagar:,.0f}"

      mensaje_encoded = urllib.parse.quote(mensaje_wa)
      whatsapp_url = f"https://wa.me/{whatsapp_numero}?text={mensaje_encoded}"

      st.markdown("---")
      st.subheader("3. Enviar a WhatsApp")
      st.markdown(
          "Haz clic en el botón para enviar el comprobante y detalle del"
          f" pedido al WhatsApp del restaurante: [📲 Enviar Pedido por"
          f" WhatsApp]({whatsapp_url})"
      )