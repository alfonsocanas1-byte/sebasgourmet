import streamlit as st
import pandas as pd
import urllib.parse
from datetime import datetime

class SebasGourmetApp:
    def __init__(self):
        self.WHATSAPP_NUM = "573128942010"
        self.PRECIOS = {
            "Carne Asada (300 gr)": 6500,
            "Porción Arroz": 2800,
            "Porción Fríjoles": 3200,
            "Porción Patacón": 3100,
            "Porción Aguacate": 3400,
            "Bebida del Día": 3000
        }
        self.inicializar_sesion()

    def inicializar_sesion(self):
        if 'pedidos_totales' not in st.session_state:
            st.session_state.pedidos_totales = []
        if 'plato_actual' not in st.session_state:
            st.session_state.plato_actual = []

    def enviar_whatsapp(self, nombre, direccion, zona, total):
        mensaje = f"🍽️ *NUEVO PEDIDO: SEBAS GOURMET*\n\n"
        mensaje += f"👤 *Cliente:* {nombre}\n"
        mensaje += f"📍 *Dirección:* {direccion}\n"
        mensaje += f"🗺️ *Zona:* {zona}\n"
        mensaje += f"📅 *Fecha:* {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
        mensaje += "\n--- *DETALLE DEL PEDIDO* ---\n"
        
        for idx, plato in enumerate(st.session_state.pedidos_totales, 1):
            mensaje += f"\n*Plato {idx}:*\n"
            for ing in plato:
                mensaje += f"  - {ing['item']} (${ing['precio']:,})\n"
        
        mensaje += f"\n🛵 *Domicilio:* {'$8,000' if zona == 'Centenario - Unicentro' else '$13,000'}\n"
        mensaje += f"💰 *TOTAL A PAGAR: ${total:,}*"
        
        texto_url = urllib.parse.quote(mensaje)
        return f"https://wa.me/{self.WHATSAPP_NUM}?text={texto_url}"

    def render_ui(self):
        st.set_page_config(page_title="Sebas Gourmet", layout="wide")
        
        # Bienvenida y Metodología
        st.title("🍽️ Bienvenido a Restaurante Sebas Gourmet")
        st.info("**Metodología:** Arma tu pedido plato por plato. Selecciona los ingredientes para tu primer plato, agrégalo al pedido y repite el proceso si deseas pedir más platos. Al finalizar, confirma tu zona para el cálculo del domicilio.")

        # Registro de Cliente
        st.subheader("1. Información de Entrega")
        col_c1, col_c2 = st.columns(2)
        nombre = col_c1.text_input("Nombre y Apellido")
        direccion = col_c2.text_input("Dirección Domicilio")
        
        st.markdown("---")
        
        col_izq, col_der = st.columns([0.6, 0.4])

        with col_izq:
            st.subheader("2. Armar Plato")
            st.write("Selecciona los ingredientes para este plato:")
            
            for item, precio in self.PRECIOS.items():
                if st.button(f"➕ {item} (${precio:,})"):
                    st.session_state.plato_actual.append({"item": item, "precio": precio})
                    st.toast(f"Agregado: {item}")

            if st.session_state.plato_actual:
                st.write("**Ingredientes en este plato:**")
                for ing in st.session_state.plato_actual:
                    st.write(f"- {ing['item']}")
                
                if st.button("📥 FINALIZAR ESTE PLATO Y AGREGAR AL PEDIDO"):
                    st.session_state.pedidos_totales.append(list(st.session_state.plato_actual))
                    st.session_state.plato_actual = []
                    st.success("Plato agregado con éxito. ¡Puedes armar otro!")
                    st.rerun()

        with col_der:
            st.subheader("📋 Resumen del Pedido")
            if st.session_state.pedidos_totales:
                subtotal_comida = 0
                for i, plato in enumerate(st.session_state.pedidos_totales, 1):
                    with st.expander(f"Plato {i}", expanded=True):
                        for ing in plato:
                            st.write(f"{ing['item']} - ${ing['precio']:,}")
                            subtotal_comida += ing['precio']
                
                st.markdown("---")
                zona = st.radio("Seleccione zona de envío:", 
                                ["Centenario - Unicentro", "Zona Alejada (+ $5.000 extra)"])
                
                costo_domicilio = 8000 if zona == "Centenario - Unicentro" else 13000
                total_final = subtotal_comida + costo_domicilio
                
                st.metric("Subtotal Comida", f"${subtotal_comida:,}")
                st.metric("Costo Domicilio", f"${costo_domicilio:,}")
                st.subheader(f"TOTAL: ${total_final:,}")

                if st.button("🚀 ENVIAR PEDIDO POR WHATSAPP"):
                    if nombre and direccion:
                        url = self.enviar_whatsapp(nombre, direccion, zona, total_final)
                        st.markdown(f'<a href="{url}" target="_blank"><button style="width:100%; background-color:#25D366; color:white; border:none; padding:12px; border-radius:8px; font-weight:bold; cursor:pointer;">CONFIRMAR EN WHATSAPP</button></a>', unsafe_allow_html=True)
                    else:
                        st.error("Por favor completa nombre y dirección.")
                
                if st.button("🗑️ Vaciar Todo"):
                    st.session_state.pedidos_totales = []
                    st.session_state.plato_actual = []
                    st.rerun()
            else:
                st.write("No has agregado platos aún.")

if __name__ == "__main__":
    app = SebasGourmetApp()
    app.render_ui()