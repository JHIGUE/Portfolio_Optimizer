import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
import plotly.graph_objects as go
import io
import os
from datetime import datetime

from data_loader import load_data
from engine import run_optimization, calculate_sequential_gantt, run_monte_carlo

# --- CONFIG ---
st.set_page_config(page_title="Strategic Portfolio Optimizer", layout="wide")
st.markdown("<style>.stTabs [data-baseweb='tab-list'] {gap: 10px;}</style>", unsafe_allow_html=True)

if 'escenarios' not in st.session_state: st.session_state['escenarios'] = []
HISTORY_FILE = "historial_decisiones.csv"

def save_history(name, budget, hours, score, cost, time, items):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M")
    df_new = pd.DataFrame([{'Fecha': ts, 'Escenario': name, 'Presupuesto': budget, 'Horas': hours, 'Valor': score, 'Coste': cost, 'Tiempo_Real': time, 'Items': items}])
    if not os.path.exists(HISTORY_FILE): df_new.to_csv(HISTORY_FILE, index=False)
    else: df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

# --- CARGA ---
current_dir = os.path.dirname(os.path.abspath(__file__))
archivo = os.path.join(current_dir, "Roadmap_2026_CORREGIDO.xlsx")
hoja = "4_Actividades_Priorizadas" 

try:
    df, _ = load_data(archivo, hoja)
    if df.empty: 
        st.error("⚠️ Error: Datos vacíos o formato incorrecto.")
        st.stop()
except Exception as e:
    st.error(f"Error carga: {e}")
    st.stop()

# --- SIDEBAR ---
st.sidebar.header("🕹️ Strategic Controls")
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

# --- MOTOR ---
df_opt = run_optimization(df, budget, hours_total)
val = df_opt['Score_Real'].sum()

# --- DASHBOARD ---
st.title("Strategic Portfolio Optimizer (SPO)")
st.caption(f"Roadmap 2026 | Modelo Ponderado (Empleabilidad + Capa + Facilidad)")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Valor Estratégico (Real)", f"{val:.1f}")
k2.metric("Inversión", f"{df_opt['Coste'].sum()} €", delta=f"{budget - df_opt['Coste'].sum()} € libre")
k3.metric("Tiempo", f"{df_opt['Horas'].sum()} h", delta=f"{hours_total - df_opt['Horas'].sum()} h libre")
k4.metric("Items", len(df_opt))

tabs = st.tabs(["🎯 Plan", "📅 Gantt", "📈 Frontera", "🔍 Auditoría Avanzada", "🎲 Riesgo", "🆚 Comparador", "📥 Exportar"])

with tabs[0]: # PLAN
    c1, c2 = st.columns([2,1])
    with c1:
        df['Estado'] = np.where(df.index.isin(df_opt.index), 'SI', 'NO')
        # Scatter ahora usa Capa_desc para colorear o dar forma si quieres, o mantenemos Estado
        fig = px.scatter(df, x="Coste", y="Score_Real", color="Estado", size="Horas", 
                         hover_data=['Actividad', 'Capa_desc', 'Probabilidad_Acumulada'], 
                         color_discrete_map={'SI':'#00CC96', 'NO':'#EF553B'},
                         title="Matriz de Valor Real vs Coste")
        st.plotly_chart(fig, use_container_width=True)
    with c2:
        st.markdown("###### Top Selección por Eficiencia")
        st.dataframe(df_opt[['Actividad', 'Capa_desc', 'Score_Real', 'ROI']].sort_values(by='ROI', ascending=False), hide_index=True)

with tabs[1]: # GANTT
    gantt = calculate_sequential_gantt(df_opt, hours_week)
    if not gantt.empty:
        # Coloreamos por Capa (Taxonomía) para ver la estrategia visualmente
        color_col = 'Capa_desc' if 'Capa_desc' in gantt.columns else 'Tipo'
        fig_g = px.timeline(gantt, x_start="Inicio", x_end="Fin", y="Tarea", color=color_col, hover_data=['Pre_req', 'Prioridad_Calc'])
        fig_g.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_g, use_container_width=True)
        st.success(f"📅 Fin Estimado: **{gantt['Fin'].max().strftime('%d/%m/%Y')}**")
    else: st.info("Sin tareas seleccionadas.")

with tabs[2]: # FRONTERA (NUEVO)
    st.markdown("### 📈 Frontera de Eficiencia de Pareto")
    st.markdown("Este gráfico responde a: *¿Cuánto valor extra gano realmente si invierto más dinero?*")
    
    if st.button("🚀 Calcular Frontera de Eficiencia"):
        # Simulamos rangos de presupuesto (desde 0 hasta el doble del actual o 2000€)
        max_b = max(2000, budget * 2)
        steps = np.linspace(0, max_b, 20)
        
        data_frontier = []
        pbar = st.progress(0)
        
        for i, b_sim in enumerate(steps):
            # Ejecutamos el motor para cada escenario hipotético
            # Mantenemos las horas fijas, solo variamos dinero para ver la curva financiera
            r = run_optimization(df, b_sim, hours_total)
            data_frontier.append({
                'Presupuesto': b_sim, 
                'Valor': r['Score_Real'].sum(),
                'Coste_Real': r['Coste'].sum()
            })
            pbar.progress((i+1)/20)
            
        df_front = pd.DataFrame(data_frontier)
        
        # 1. Pintamos la Línea (Curva de Pareto)
        fig_f = px.line(df_front, x="Coste_Real", y="Valor", markers=True, 
                        title="Curva de Retorno de Inversión (ROI Estratégico)", 
                        labels={"Coste_Real": "Inversión (€)", "Valor": "Valor Estratégico Total"})
        
        # 2. Pintamos TU Posición Actual (Estrella Roja)
        fig_f.add_trace(go.Scatter(
            x=[df_opt['Coste'].sum()], 
            y=[val],
            mode='markers',
            marker=dict(color='red', size=15, symbol='star'),
            name="Tu Plan Actual"
        ))
        
        st.plotly_chart(fig_f, use_container_width=True)
        st.info("💡 **Interpretación:** Si la curva se aplana, significa que gastar más dinero ya no aporta valor significativo (has comprado todo lo 'bueno'). El punto rojo indica dónde estás tú respecto al óptimo matemático.")

with tabs[3]: # AUDITORÍA (ACTUALIZADA)
    st.markdown("### 🕵️ Auditoría del Algoritmo")
    st.markdown("Desglose del cálculo de `Score_Base` y `Probabilidad_Acumulada`.")
    
    # Columnas clave para auditar el nuevo modelo
    audit_cols = ['ID', 'Actividad', 'Capa_desc', 'Empleabilidad', 'Facilidad', 'Capa_score', 
                  'Score_Base', 'Probabilidad', 'Probabilidad_Acumulada', 'Score_Real']
    
    # Filtramos solo columnas que existan
    cols_to_show = [c for c in audit_cols if c in df.columns]
    
    st.dataframe(
        df[cols_to_show].sort_values(by='Score_Real', ascending=False), 
        use_container_width=True,
        column_config={
            "Score_Base": st.column_config.NumberColumn(format="%.2f"),
            "Probabilidad_Acumulada": st.column_config.ProgressColumn(format="%.2f", min_value=0, max_value=1),
            "Score_Real": st.column_config.NumberColumn(format="%.2f", help="Base * Prob. Acumulada")
        }
    )

with tabs[4]: # RIESGO
    if st.button("Lanzar Simulación Monte Carlo"):
        mc = run_monte_carlo(df_opt)
        
        # 1. Gráficos Visuales
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.histogram(mc, x="Horas", title="Riesgo de Tiempo (Prob. Individual)"), use_container_width=True)
        c2.plotly_chart(px.histogram(mc, x="Valor", title="Valor Esperado (Score Base)"), use_container_width=True)
        
        # 2. Interpretación en Lenguaje Natural (RECUPERADO)
        # Calculamos percentiles clave
        p50_hours = np.percentile(mc['Horas'], 50) # Mediana (lo más probable)
        p90_hours = np.percentile(mc['Horas'], 90) # Caso pesimista (90% de certeza)
        p10_value = np.percentile(mc['Valor'], 10) # Caso pesimista de valor (mínimo garantizado al 90%)
        avg_value = mc['Valor'].mean()
        
        st.divider()
        st.markdown("### 🧠 Interpretación de Escenarios")
        st.info(f"""
        **⏱️ Sobre el Tiempo:**
        * **Lo más probable (Escenario Realista):** El proyecto te tomará unas **{int(p50_hours)} horas**.
        * **El riesgo (Escenario Pesimista):** Hay un 10% de posibilidades de que se complique hasta las **{int(p90_hours)} horas** debido a la incertidumbre.
        
        **💎 Sobre el Valor:**
        * **Suelo de Seguridad:** Incluso si muchas tareas fallan (Probabilidad), tienes un 90% de certeza de conseguir al menos **{p10_value:.1f} puntos** de valor estratégico.
        * **Valor Esperado:** De media, este plan aporta **{avg_value:.1f} puntos**.
        """)

with tabs[5]: # COMPARADOR
    if st.session_state['escenarios']:
        cdf = pd.DataFrame(st.session_state['escenarios'])
        st.dataframe(cdf, use_container_width=True)
        st.plotly_chart(px.bar(cdf, x='Nombre', y='Valor', color='Coste'), use_container_width=True)
    else: st.info("Añade escenarios.")

with tabs[6]: # EXPORTAR
    if not df_opt.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_opt.to_excel(writer, sheet_name='Plan_Optimizado', index=False)
        st.download_button("📥 Descargar Plan", buffer.getvalue(), "Plan_SPO.xlsx")


