import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import io
import os
from datetime import datetime, timedelta

# --- IMPORTAMOS MÓDULOS PROPIOS ---
from data_loader import load_data
from engine import run_optimization, calculate_sequential_gantt, run_monte_carlo

# --- CONFIG ---
st.set_page_config(page_title="Strategic Portfolio Optimizer", layout="wide")
st.markdown("<style>.stTabs [data-baseweb='tab-list'] {gap: 10px;}</style>", unsafe_allow_html=True)

# --- ESTADO ---
if 'escenarios' not in st.session_state: st.session_state['escenarios'] = []
HISTORY_FILE = "historial_decisiones.csv"

def save_history(name, budget, hours, score, cost, time, items):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([{'Fecha': ts, 'Escenario': name, 'Presupuesto': budget, 'Horas': hours, 'Valor': score, 'Coste': cost, 'Tiempo_Real': time, 'Items': items}])
    if not os.path.exists(HISTORY_FILE): df_new.to_csv(HISTORY_FILE, index=False)
    else: df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

def load_history_df():
    if os.path.exists(HISTORY_FILE): return pd.read_csv(HISTORY_FILE)
    return pd.DataFrame()

# --- UI ---
archivo = "Roadmap_2026_CORREGIDO.xlsx" # Asegúrate que el archivo está en la misma carpeta
hoja = "4_Actividades_Priorizadas"

try:
    df, df_audit = load_data(archivo, hoja)
    if df.empty: st.error("No hay datos"); st.stop()
except: st.stop()

# SIDEBAR
st.sidebar.header("🕹️ Controles de Estrategia")
budget = st.sidebar.slider("💰 Presupuesto (€)", 0, 10000, 650, step=50)
hours_total = st.sidebar.slider("⏳ Bolsa Horas Anual", 0, 2000, 300, step=10)
hours_week = st.sidebar.number_input("Velocidad (Horas/Semana)", 1, 40, 10)

st.sidebar.divider()
sc_name = st.sidebar.text_input("Nombre Escenario", "Escenario A")
if st.sidebar.button("💾 Comparar Escenario"):
    opt_res = run_optimization(df, budget, hours_total)
    st.session_state['escenarios'].append({'Nombre': sc_name, 'Valor': opt_res['Score_Real'].sum(), 'Coste': opt_res['Coste'].sum(), 'Horas': opt_res['Horas'].sum()})
    st.sidebar.success("Guardado en Comparador")

if st.sidebar.button("📜 Guardar en Historial (CSV)"):
    opt_res = run_optimization(df, budget, hours_total)
    save_history(sc_name, budget, hours_total, opt_res['Score_Real'].sum(), opt_res['Coste'].sum(), opt_res['Horas'].sum(), len(opt_res))
    st.sidebar.success("Guardado en Disco")

if st.sidebar.button("🗑️ Limpiar Comparador"): st.session_state['escenarios'] = []

# MAIN
df_opt = run_optimization(df, budget, hours_total)
val = df_opt['Score_Real'].sum()

st.title("Strategic Portfolio Optimizer (SPO)")
st.caption("AI-Driven Decision Engine for Resource Allocation")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Valor Estratégico", f"{val:.1f}")
k2.metric("Inversión", f"{df_opt['Coste'].sum()} €", delta=f"Restante: {budget - df_opt['Coste'].sum()}")
k3.metric("Tiempo Estimado", f"{df_opt['Horas'].sum()} h", delta=f"Restante: {hours_total - df_opt['Horas'].sum()}")
k4.metric("Actividades", len(df_opt))

tabs = st.tabs(["🎯 Plan", "📅 Gantt", "🆚 Comparador", "🎲 Riesgo", "🔍 Auditoría", "📥 Exportar"])

with tabs[0]: # PLAN
    c1, c2 = st.columns([2,1])
    with c1:
        # CORRECCIÓN: Usamos 'df' (limpio) en lugar de 'df_audit' (crudo)
        # porque 'df' es el que tiene las columnas 'Score_Real' y 'Coste' calculadas.
        df['Estado'] = np.where(df.index.isin(df_opt.index), 'SI', 'NO')
        
        fig = px.scatter(df, x="Coste", y="Score_Real", color="Estado", size="Horas", 
                         hover_data=['Actividad'], 
                         color_discrete_map={'SI':'#00CC96', 'NO':'#EF553B'},
                         title="Matriz de Valor vs Coste")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.dataframe(df_opt[['Actividad', 'Coste', 'Eficiencia']].sort_values(by='Eficiencia', ascending=False), hide_index=True)

with tabs[1]: # GANTT
    gantt_df = calculate_sequential_gantt(df_opt, hours_week)
    if not gantt_df.empty:
        fig_g = px.timeline(gantt_df, x_start="Inicio", x_end="Fin", y="Tarea", color="Tipo", hover_data=['Pre_req'])
        fig_g.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_g, use_container_width=True)
    else: st.warning("Sin datos para Gantt")

with tabs[2]: # COMPARADOR
    if st.session_state['escenarios']:
        cdf = pd.DataFrame(st.session_state['escenarios'])
        st.dataframe(cdf, use_container_width=True)
        st.plotly_chart(px.bar(cdf, x='Nombre', y='Valor', color='Coste', title="Valor vs Coste"), use_container_width=True)

with tabs[3]: # RIESGO
    if st.button("Lanzar Monte Carlo"):
        mc = run_monte_carlo(df_opt)
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.histogram(mc, x="Horas", title="Distribución de Tiempo"), use_container_width=True)
        c2.plotly_chart(px.histogram(mc, x="Valor", title="Distribución de Valor"), use_container_width=True)

with tabs[4]: # AUDITORÍA
    st.dataframe(df_audit, use_container_width=True)

with tabs[5]: # EXPORTAR
    if not df_opt.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_opt.to_excel(writer, sheet_name='Plan', index=False)

        st.download_button("📥 Excel", buffer.getvalue(), "Plan.xlsx")
