import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io
import os
from datetime import datetime

# --- IMPORTAMOS TUS MÓDULOS ---
from data_loader import load_data
from engine import run_optimization, calculate_sequential_gantt, run_monte_carlo

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Strategic Portfolio Optimizer", layout="wide")
st.markdown("<style>.stTabs [data-baseweb='tab-list'] {gap: 10px;}</style>", unsafe_allow_html=True)

# --- ESTADO Y PERSISTENCIA ---
if 'escenarios' not in st.session_state: st.session_state['escenarios'] = []
HISTORY_FILE = "historial_decisiones.csv"

def save_history(name, budget, hours, score, cost, time, items):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([{'Fecha': ts, 'Escenario': name, 'Presupuesto': budget, 'Horas': hours, 'Valor': score, 'Coste': cost, 'Tiempo_Real': time, 'Items': items}])
    if not os.path.exists(HISTORY_FILE): df_new.to_csv(HISTORY_FILE, index=False)
    else: df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

# --- CARGA DE DATOS ---
archivo = "Roadmap_2026_CORREGIDO.xlsx"
hoja = "4_Actividades_Priorizadas" # ¡Asegúrate que tu hoja se llama así!

try:
    # Ahora load_data devuelve dos dataframes iguales y limpios
    df, _ = load_data(archivo, hoja)
    if df.empty: 
        st.error("⚠️ No se pudieron leer los datos. Revisa que el Excel tenga las columnas: ID, Actividad, Coste, Horas, Score, Pre_req, Probabilidad.")
        st.stop()
except Exception as e:
    st.error(f"Error crítico: {e}")
    st.stop()

# --- SIDEBAR (CONTROLES) ---
st.sidebar.header("🕹️ Controles de Estrategia")
budget = st.sidebar.slider("💰 Presupuesto (€)", 0, 10000, 650, step=50)
hours_total = st.sidebar.slider("⏳ Bolsa Horas Anual", 0, 2000, 300, step=10)
hours_week = st.sidebar.number_input("Velocidad (Horas/Semana)", 1, 40, 10)

st.sidebar.divider()
sc_name = st.sidebar.text_input("Nombre Escenario", "Escenario A")
c1, c2 = st.sidebar.columns(2)
if c1.button("💾 Comparar"):
    res = run_optimization(df, budget, hours_total)
    st.session_state['escenarios'].append({'Nombre': sc_name, 'Valor': res['Score_Real'].sum(), 'Coste': res['Coste'].sum()})
    st.sidebar.success("Añadido")

if c2.button("📜 Historial"):
    res = run_optimization(df, budget, hours_total)
    save_history(sc_name, budget, hours_total, res['Score_Real'].sum(), res['Coste'].sum(), res['Horas'].sum(), len(res))
    st.sidebar.success("Guardado")

if st.sidebar.button("🗑️ Reset"): st.session_state['escenarios'] = []

# --- MOTOR PRINCIPAL ---
df_opt = run_optimization(df, budget, hours_total)
val = df_opt['Score_Real'].sum()

# --- DASHBOARD ---
st.title("Strategic Portfolio Optimizer (SPO)")
st.caption("AI-Driven Resource Allocation Engine")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Valor Estratégico", f"{val:.1f}")
k2.metric("Inversión", f"{df_opt['Coste'].sum()} €", delta=f"{budget - df_opt['Coste'].sum()} € rest")
k3.metric("Tiempo", f"{df_opt['Horas'].sum()} h", delta=f"{hours_total - df_opt['Horas'].sum()} h rest")
k4.metric("Actividades", len(df_opt))

tabs = st.tabs(["🎯 Plan", "📅 Gantt", "🆚 Comparador", "🎲 Riesgo", "🔍 Auditoría", "📥 Exportar"])

with tabs[0]: # PLAN
    c1, c2 = st.columns([2,1])
    with c1:
        # Calculamos estado para colorear
        df['Estado'] = np.where(df.index.isin(df_opt.index), 'SI', 'NO')
        
        # --- CORRECCIONES APLICADAS ---
        # 1. Eje X cambiado a "Horas".
        # 2. Corregido typo "Hpras" -> "Horas". 
        #    NOTA: No uses "Coste" para el tamaño (size), porque las actividades gratuitas (0€) desaparecerían del mapa.
        # 3. Añadido hover_data para que sigas viendo el Coste al pasar el ratón.
        
        fig = px.scatter(df, 
                         x="Horas", 
                         y="Score_Real", 
                         color="Estado", 
                         size="Horas", # Burbuja grande = Más horas (visible siempre porque horas > 0)
                         hover_data=['Actividad', 'Coste', 'Probabilidad'], 
                         color_discrete_map={'SI':'#00CC96', 'NO':'#EF553B'},
                         title="Matriz Valor (Y) vs Esfuerzo (X)")
        
        # Ajuste para que el eje X no empiece pegado al borde si hay valores bajos
        fig.update_layout(xaxis_title="Horas de Dedicación", yaxis_title="Score Real (Valor)")
        
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Selección por Tiempo")
        # --- CORRECCIÓN TABLA ---
        # Cambiado 'Coste' por 'Horas' para que sea coherente con el gráfico
        st.dataframe(
            df_opt[['Actividad', 'Horas', 'Eficiencia']]
            .sort_values(by='Eficiencia', ascending=False), 
            hide_index=True
        )
        
with tabs[1]: # GANTT
    gantt = calculate_sequential_gantt(df_opt, hours_week)
    if not gantt.empty:
        fig_g = px.timeline(gantt, x_start="Inicio", x_end="Fin", y="Tarea", color="Tipo", hover_data=['Pre_req'])
        fig_g.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_g, use_container_width=True)
    else: st.info("No hay tareas seleccionadas")

with tabs[2]: # COMPARADOR
    if st.session_state['escenarios']:
        cdf = pd.DataFrame(st.session_state['escenarios'])
        st.dataframe(cdf, use_container_width=True)
        st.plotly_chart(px.bar(cdf, x='Nombre', y='Valor', color='Coste'), use_container_width=True)

with tabs[3]: # RIESGO
    if st.button("Lanzar Monte Carlo"):
        mc = run_monte_carlo(df_opt)
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.histogram(mc, x="Horas"), use_container_width=True)
        c2.plotly_chart(px.histogram(mc, x="Valor"), use_container_width=True)

with tabs[4]: # AUDITORÍA
    st.dataframe(df, use_container_width=True)

with tabs[5]: # EXPORTAR
    if not df_opt.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_opt.to_excel(writer, sheet_name='Plan', index=False)
        st.download_button("📥 Descargar Excel", buffer.getvalue(), "Plan.xlsx")