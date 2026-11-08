# sebasgourmet.py
from datetime import datetime
import random
import urllib.parse
import pandas as pd
import streamlit as st
from supabase import create_client

# Configuración de la página
st.set_page_config(
    page_title="Sebas Gourmet - Pedidos", page_icon="🍲", layout="centered"
)

# ==========================================
# CREDENCIALES REALES DE SUPABASE
# ==========================================
SUPABASE_URL = "https://jvkjcdyrheizomzjzhpw.supabase.co"
SUPABASE_KEY = "sb_publishable_cdNJF9NVFMomNUh72Yiujw_0EEdYowz"

try:
  supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
except Exception as e:
  st.error(f"Error al conectar con Supabase: {e}")

# Título principal y Fecha en la parte superior
st.title("🍲 Sebas Gourmet")
st.markdown(
    "### Sistema de Gestión de Almuerzos y Platos Especiales/Eventos"
)

fecha_actual_header = datetime.now().strftime("%Y-%m-%d")
st.markdown(f"📅 **Fecha de hoy:** {fecha_actual_header}")
st.markdown("---")

# Menú disponible y precios en COP (Actualizado con plato gourmet mediano y pequeño)
MENU = {
    "Costilla de cerdo a la bbq más acompañantes": 22000,
    "Pollo en salsa de champiñones más acompañantes": 17000,
    "Carne de res asada más acompañantes": 17000,
    "Arroz con pollo más acompañantes": 17000,
    "Plato gourmet mediano": 100000,
    "Plato gourmet pequeño": 50000,
}

with st.form("form_sebas_gourmet"):
  st.subheader("1. Datos del Cliente y Envío")
  nombre = st.text_input("Nombre cliente")
  telefono = st.text_input("Número celular (ej. 3128942010)")
  tipo_entrega = st.selectbox(
      "Tipo de entrega", ["Domicilio", "Para recoger en local", "Evento"]
  )
  estado_pedido = st.selectbox(
      "Estado inicial del pedido", ["Pedido", "En fabricación", "Entregado"]
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
                "precio plato": MENU[plato],
                "cantidad": cant,
                "total por plato": cant * MENU[plato],
            }
        )

    if not platos_seleccionados:
      st.warning("Debes seleccionar al menos un plato para realizar el pedido.")
    else:
      # Generar número de pedido y fecha actual
      numero_pedido = random.randint(10000, 99999)
      fecha_actual = datetime.now().strftime("%Y-%m-%d")
      fecha_hora_texto = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

      # Cálculos generales
      total_platos_variedad = len(platos_seleccionados)
      total_pedido_general = sum(
          item["total por plato"] for item in platos_seleccionados
      )

      # 2. Insertar cada plato como una fila en la tabla 'Pedidosebasgourmet' de Supabase
      try:
        registros_a_insertar = []
        for item in platos_seleccionados:
          fila = {
              "número pedido": numero_pedido,
              "fecha de pedido": fecha_actual,
              "nombre cliente": nombre,
              "número celular": int(telefono),
              "tipo de entrega": tipo_entrega,
              "nombre plato": item["nombre plato"],
              "precio plato": item["precio plato"],
              "cantidad": item["cantidad"],
              "total por plato": item["total por plato"],
              "total platos": total_platos_variedad,
              "total pedido": total_pedido_general,
              "estado": estado_pedido,
          }
          registros_a_insertar.append(fila)

        supabase.table("Pedidosebasgourmet").insert(
            registros_a_insertar
        ).execute()
        st.success(
            "¡Pedido registrado exitosamente en la base de datos con el N°"
            f" {numero_pedido}!"
        )
      except Exception as e:
        st.error(f"Error al guardar en la base de datos de Supabase: {e}")

      # ==========================================
      # 3. RECIBO / RESUMEN EN PANTALLA
      # ==========================================
      st.markdown("---")
      st.markdown("### 🧾 Recibo del Pedido Actual")
      st.info(
          f"**Pedido N°:** {numero_pedido}\n\n"
          f"📅 **Fecha y Hora:** {fecha_hora_texto}\n"
          f"👤 **Cliente:** {nombre}\n"
          f"📞 **Celular:** {telefono}\n"
          f"📦 **Tipo de Entrega:** {tipo_entrega}\n"
          f"📌 **Estado:** {estado_pedido}\n"
      )

      st.markdown("**Detalle de Platos:**")
      for item in platos_seleccionados:
        st.write(
            f"- {item['cantidad']}x {item['nombre plato']} | V. Unit:"
            f" ${item['precio plato']:,.0f} | Subtotal:"
            f" **${item['total por plato']:,.0f}**"
        )

      st.markdown(f"### 💰 Total a Pagar: ${total_pedido_general:,.0f}")

      # 4. Construir mensaje detallado para WhatsApp (Número: 3128942010)
      whatsapp_numero = "573128942010"
      mensaje_wa = (
          f"¡Hola Sebas Gourmet! 🍽️ Nuevo Pedido N° {numero_pedido}:\n\n"
          f"📅 *Fecha:* {fecha_hora_texto}\n"
          f"👤 *Cliente:* {nombre}\n"
          f"📞 *Celular:* {telefono}\n"
          f"📦 *Tipo de entrega:* {tipo_entrega}\n"
          f"📌 *Estado:* {estado_pedido}\n\n"
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
      st.subheader("4. Enviar a WhatsApp")
      st.markdown(
          "Haz clic en el botón para enviar el comprobante y detalle del"
          f" pedido al WhatsApp del restaurante: [📲 Enviar Pedido por"
          f" WhatsApp]({whatsapp_url})"
      )

# ==========================================
# 5. GESTIÓN Y CAMBIO DE ESTADO DE PEDIDOS
# ==========================================
st.markdown("---")
st.subheader("⚙️ Actualizar Estado de un Pedido")

try:
  response_check = supabase.table("Pedidosebasgourmet").select("*").execute()
  if response_check.data:
    df_check = pd.DataFrame(response_check.data)

    col_num_pedido = [
        c
        for c in df_check.columns
        if "número" in c.lower() or "numero" in c.lower()
    ]

    if col_num_pedido:
      nombre_columna = col_num_pedido[0]
      df_check = df_check.dropna(subset=[nombre_columna])
      numeros_unicos = sorted(df_check[nombre_columna].unique().tolist())

      if numeros_unicos:
        with st.form("form_actualizar_estado"):
          col1, col2, col3 = st.columns(3)
          with col1:
            pedido_seleccionado = st.selectbox(
                "Seleccione N° de Pedido", numeros_unicos
            )
          with col2:
            nuevo_estado = st.selectbox(
                "Nuevo Estado", ["Pedido", "En fabricación", "Entregado"]
            )
          with col3:
            st.write("")
            st.write("")
            btn_actualizar = st.form_submit_button("Guardar Estado en Supabase")

        if btn_actualizar:
          try:
            supabase.table("Pedidosebasgourmet").update(
                {"estado": nuevo_estado}
            ).eq(nombre_columna, int(pedido_seleccionado)).execute()
            st.success(
                f"¡El estado del pedido N° {pedido_seleccionado} fue actualizado"
                f" a '{nuevo_estado}' con éxito!"
            )
            st.rerun()
          except Exception as e:
            st.error(f"Error al actualizar el estado en Supabase: {e}")
      else:
        st.info("No hay números de pedido válidos para modificar.")
    else:
      st.error("No se encontró la columna de número de pedido en la tabla.")
  else:
    st.info("No hay pedidos registrados en la base de datos todavía.")
except Exception as e:
  st.error(f"Error al conectar para actualizar estados: {e}")

# ==========================================
# 6. MOSTRAR TABLA DE PEDIDOS REGISTRADOS
# ==========================================
st.markdown("---")
st.subheader("📋 Historial de Pedidos en Supabase")

try:
  response = supabase.table("Pedidosebasgourmet").select("*").execute()
  registros = response.data

  if registros:
    df_pedidos = pd.DataFrame(registros)
    st.dataframe(df_pedidos, use_container_width=True)
  else:
    st.info("Aún no hay pedidos registrados en la base de datos.")
except Exception as e:
  st.error(f"No se pudo cargar la tabla de pedidos desde Supabase: {e}")