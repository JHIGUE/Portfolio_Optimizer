import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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
    b_val = budget if budget is not None else "Ilimitado"
    df_new = pd.DataFrame([{'Fecha': ts, 'Escenario': name, 'Presupuesto': b_val, 'Horas': hours, 'Valor': score, 'Coste': cost, 'Tiempo_Real': time, 'Items': items}])
    if not os.path.exists(HISTORY_FILE): df_new.to_csv(HISTORY_FILE, index=False)
    else: df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

# --- CARGA DE DATOS ---
current_dir = os.path.dirname(os.path.abspath(__file__))
archivo = os.path.join(current_dir, "Roadmap_2026_CORREGIDO.xlsx")
hoja = "4_Actividades_Priorizadas" 

try:
    df, _ = load_data(archivo, hoja)
    if df.empty: 
        st.error("⚠️ No se pudieron leer los datos. Revisa el Excel.")
        st.stop()
except Exception as e:
    st.error(f"Error crítico: {e}")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("🕹️ Controles de Estrategia")
hours_total = st.sidebar.slider("⏳ Tu Tiempo (Bolsa Horas Anual)", 0, 1000, 300, step=10)
hours_week = st.sidebar.number_input("Velocidad (Horas/Semana)", 1, 40, 10)

st.sidebar.divider()

use_budget = st.sidebar.checkbox("🔒 Activar límite de Presupuesto", value=False)
if use_budget:
    budget = st.sidebar.slider("💰 Presupuesto Máximo (€)", 0, 5000, 600, step=50)
else:
    budget = None
    st.sidebar.caption("✅ Presupuesto ilimitado.")

st.sidebar.divider()

sc_name = st.sidebar.text_input("Nombre Escenario", "Escenario A")
c1, c2 = st.sidebar.columns(2)
if c1.button("💾 Comparar"):
    res = run_optimization(df, hours_total, budget)
    st.session_state['escenarios'].append({'Nombre': sc_name, 'Valor': res['Score_Real'].sum(), 'Coste': res['Coste'].sum()})
    st.sidebar.success("Añadido")

if c2.button("📜 Historial"):
    res = run_optimization(df, hours_total, budget)
    save_history(sc_name, budget, hours_total, res['Score_Real'].sum(), res['Coste'].sum(), res['Horas'].sum(), len(res))
    st.sidebar.success("Guardado")

if st.sidebar.button("🗑️ Reset"): st.session_state['escenarios'] = []

# --- MOTOR PRINCIPAL ---
df_opt = run_optimization(df, hours_total, budget)
val = df_opt['Score_Real'].sum()
coste_real = df_opt['Coste'].sum()

# --- DASHBOARD ---
st.title("Strategic Portfolio Optimizer (SPO)")
st.caption(f"Roadmap 2026 | Estrategia 'Time-First' & 'Leader Risk Mitigation'")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Valor Estratégico", f"{val:.1f}")
k2.metric("Tiempo Usado", f"{df_opt['Horas'].sum()} h", delta=f"{hours_total - df_opt['Horas'].sum()} h libres")
delta_color = "normal" if (budget is None or coste_real <= budget) else "inverse"
presupuesto_str = f"/ {budget}€" if budget else "(Sin límite)"
k3.metric("Coste Resultante", f"{coste_real} €", f"vs {presupuesto_str}")
k4.metric("Actividades", len(df_opt))

# --- PESTAÑAS ---
tabs = st.tabs(["📖 Contexto", "🎯 Plan", "📅 Gantt", "📈 Curva de Valor", "🔍 Auditoría", "🎲 Riesgo", "🆚 Comparador", "📥 Exportar"])

with tabs[0]: # CONTEXTO
    st.markdown("## 🧠 Manifiesto del Algoritmo (SPO)")
    c1, c2 = st.columns(2)
    with c1:
        st.info("### 1. Time-First & Leader Risk")
        st.markdown("""
        * **Leader Risk Mitigation:** El algoritmo asume que tu seniority reduce el riesgo a la mitad. 
          `Prob_Adj = 1 - (Riesgo / 2)`.
        * **Time-First:** Priorizamos el retorno por hora invertida, no por euro gastado.
        """)
        st.latex(r'''Prob_{Adj} = 1 - \frac{(1 - Prob_{Original})}{2}''')
    with c2:
        st.success("### 2. Guía Visual")
        st.markdown("""
        * **Matriz de Valor:** Eje X es Tiempo. Burbujas grandes = Tareas largas.
        * **Gantt:** Optimizado por dependencias topológicas.
        """)

with tabs[1]: # PLAN
    c1, c2 = st.columns([2,1])
    with c1:
        # Estado
        df['Estado'] = np.where(df.index.isin(df_opt.index), 'SI', 'NO')
        
        # --- CAMBIO APLICADO: Ejes y Tamaño basados en Horas ---
        fig = px.scatter(df, 
                         x="Horas",  # EJE X: Esfuerzo en tiempo
                         y="Score_Real", # EJE Y: Valor
                         color="Estado", 
                         size="Horas", # TAMAÑO: Burbujas grandes = Tareas largas
                         hover_data=['Actividad', 'Coste', 'Probabilidad', 'Probabilidad_Original'], 
                         color_discrete_map={'SI':'#00CC96', 'NO':'#EF553B'},
                         title="Matriz Valor (Y) vs Esfuerzo en Tiempo (X)")
        
        fig.update_layout(xaxis_title="Horas de Dedicación", yaxis_title="Score Real (Valor)")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Ranking de Eficiencia (Valor/Hora)")
        # --- CAMBIO APLICADO: Tabla muestra Horas ---
        st.dataframe(
            df_opt[['Actividad', 'Horas', 'Eficiencia']]
            .sort_values(by='Eficiencia', ascending=False), 
            hide_index=True,
            column_config={
                "Eficiencia": st.column_config.NumberColumn(format="%.2f")
            }
        )

with tabs[2]: # GANTT
    gantt = calculate_sequential_gantt(df_opt, hours_week)
    if not gantt.empty:
        color_col = 'Capa_desc' if 'Capa_desc' in gantt.columns else 'Tipo'
        fig_g = px.timeline(gantt, x_start="Inicio", x_end="Fin", y="Tarea", color=color_col, hover_data=['Pre_req'])
        fig_g.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_g, use_container_width=True)
        st.success(f"📅 Fecha fin estimada: **{gantt['Fin'].max().strftime('%d/%m/%Y')}**")
    else: st.info("No hay tareas seleccionadas")

with tabs[3]: # CURVA
    st.markdown("### 📈 Análisis de Sensibilidad Temporal")
    if st.button("🚀 Calcular Curva"):
        max_h = max(1000, hours_total * 2)
        steps = np.linspace(0, max_h, 30)
        data_curve = []
        pbar = st.progress(0)
        for i, h_sim in enumerate(steps):
            r = run_optimization(df, h_sim, budget=None) 
            data_curve.append({'Horas_Disp': h_sim, 'Valor': r['Score_Real'].sum()})
            pbar.progress((i+1)/30)
        
        df_curve = pd.DataFrame(data_curve)
        fig_c = px.line(df_curve, x="Horas_Disp", y="Valor", markers=True, title="Curva de Valor vs Dedicación")
        fig_c.add_vline(x=hours_total, line_dash="dash", line_color="red")
        fig_c.add_trace(go.Scatter(x=[hours_total], y=[val], mode='markers+text', marker=dict(color='red', size=15, symbol='star'), text=["TÚ"], name="Plan Actual"))
        st.plotly_chart(fig_c, use_container_width=True)

with tabs[4]: # AUDITORÍA
    # Mostramos también la probabilidad original para verificar el ajuste
    audit_cols = ['ID', 'Actividad', 'Score_Real', 'Probabilidad', 'Probabilidad_Original', 'Eficiencia']
    cols_to_show = [c for c in audit_cols if c in df.columns]
    st.dataframe(df[cols_to_show].sort_values(by='Score_Real', ascending=False), use_container_width=True)

with tabs[5]: # RIESGO
    if st.button("Lanzar Monte Carlo"):
        mc = run_monte_carlo(df_opt)
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.histogram(mc, x="Horas", title="Distribución Tiempo"), use_container_width=True)
        c2.plotly_chart(px.histogram(mc, x="Valor", title="Distribución Valor"), use_container_width=True)

with tabs[6]: # COMPARADOR
    if st.session_state['escenarios']:
        cdf = pd.DataFrame(st.session_state['escenarios'])
        st.dataframe(cdf, use_container_width=True)
        st.plotly_chart(px.bar(cdf, x='Nombre', y='Valor', color='Coste'), use_container_width=True)
    else: st.info("Añade escenarios.")

with tabs[7]: # EXPORTAR
    if not df_opt.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_opt.to_excel(writer, sheet_name='Plan_Optimizado', index=False)
        st.download_button("📥 Descargar Plan (Excel)", buffer.getvalue(), "Plan_SPO.xlsx")