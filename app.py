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
presupuesto_str = f"/ {budget}€" if budget else "(Sin límite)"
k3.metric("Coste Resultante", f"{coste_real} €", f"vs {presupuesto_str}")
k4.metric("Actividades", len(df_opt))

# --- PESTAÑAS ---
tabs = st.tabs(["📖 Contexto", "🎯 Plan", "📅 Gantt", "📈 Curva de Valor", "🔍 Auditoría", "🎲 Riesgo", "🆚 Comparador", "📥 Exportar"])

with tabs[0]: # CONTEXTO
    st.markdown("## 🧭 Visión General del Informe")
    st.markdown("""
    Este dashboard es tu **cuadro de mando ejecutivo** para 2026. A diferencia de una lista de tareas tradicional, 
    utiliza un **algoritmo de optimización matemática (Knapsack)** que prioriza tus actividades basándose en el **retorno por hora invertida**.
    
    El sistema asume que, como líder, tu restricción principal no es el dinero, sino el **tiempo y la atención**.
    """)
    
    st.divider()
    
    col_info, col_nav = st.columns(2)
    
    with col_info:
        st.info("### 🧠 Lógica del Motor")
        st.markdown("""
        * **Leader Risk Mitigation:** El algoritmo asume que tu seniority reduce el riesgo técnico a la mitad.
          `Prob_Adj = 1 - (Riesgo / 2)`
        * **Time-First Strategy:** El eje central de decisión es la eficiencia temporal.
        """)
        st.latex(r'''Score = (Empleabilidad \times 0.4) + (Capa \times 0.4) + (Facilidad \times 0.2)''')
        
    with col_nav:
        st.success("### 📂 Guía de Pestañas")
        with st.expander("🎯 1. Plan Estratégico (Scatter & Ranking)"):
            st.write("Visualiza qué actividades entran en tu agenda (Verde) y cuáles se quedan fuera (Rojo) por falta de tiempo o valor.")
        with st.expander("📅 2. Gantt Secuencial"):
            st.write("Orden lógico de ejecución. El algoritmo adelanta tareas pequeñas que desbloquean grandes hitos.")
        with st.expander("📈 3. Curva de Valor"):
            st.write("Análisis de sensibilidad. Te dice si estudiar más horas aporta valor real o si estás saturado.")
        with st.expander("🎲 4. Riesgo (Monte Carlo)"):
            st.write("Simulación de incertidumbre. Predicción realista de tiempos aplicando la Ley de Hofstadter.")

    st.divider()
    st.markdown("### ⚙️ Taxonomía de Arquitectura 2026")
    cols = st.columns(5)
    cols[0].metric("Orchestration", "10 pts", "Core Agéntico")
    cols[1].metric("Governance", "9 pts", "Diferenciador Enterprise")
    cols[2].metric("Data & Memory", "9 pts", "Base del Conocimiento")
    cols[3].metric("Models (LLMs)", "7 pts", "Commodity Potente")
    cols[4].metric("Infrastructure", "5 pts", "Utility")

with tabs[1]: # PLAN
    st.caption("📍 **Explicación:** Las burbujas **VERDES** son las seleccionadas. Fíjate en las que están arriba a la izquierda (Alto Valor, Poco Tiempo).")
    c1, c2 = st.columns([2,1])
    with c1:
        df['Estado'] = np.where(df.index.isin(df_opt.index), 'SI', 'NO')
        fig = px.scatter(df, x="Horas", y="Score_Real", color="Estado", size="Horas", 
                         hover_data=['Actividad', 'Coste', 'Probabilidad', 'Probabilidad_Original'], 
                         color_discrete_map={'SI':'#00CC96', 'NO':'#EF553B'},
                         title="Matriz Valor (Y) vs Esfuerzo en Tiempo (X)")
        fig.update_layout(xaxis_title="Horas de Dedicación", yaxis_title="Score Real (Valor)")
        st.plotly_chart(fig, use_container_width=True)
        
        # RESTAURADO: Interpretación del Plan
        st.info(f"**Insight:** Has seleccionado **{len(df_opt)} actividades** estratégicas. Las actividades en ROJO se han descartado porque consumen demasiado tiempo para el valor que aportan comparado con las seleccionadas.")

    with c2:
        st.subheader("Ranking de Eficiencia")
        st.dataframe(df_opt[['Actividad', 'Horas', 'Eficiencia']].sort_values(by='Eficiencia', ascending=False), 
                     hide_index=True, column_config={"Eficiencia": st.column_config.NumberColumn(format="%.2f")})

with tabs[2]: # GANTT
    st.caption("🗓️ **Explicación:** Cronograma optimizado por dependencias. No intentes alterar el orden; está calculado para desbloquear valor lo antes posible.")
    gantt = calculate_sequential_gantt(df_opt, hours_week)
    if not gantt.empty:
        color_col = 'Capa_desc' if 'Capa_desc' in gantt.columns else 'Tipo'
        fig_g = px.timeline(gantt, x_start="Inicio", x_end="Fin", y="Tarea", color=color_col, hover_data=['Pre_req'])
        fig_g.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_g, use_container_width=True)
        st.success(f"📅 Fecha fin estimada: **{gantt['Fin'].max().strftime('%d/%m/%Y')}** (a ritmo de {hours_week}h/semana)")
    else: st.info("No hay tareas seleccionadas")

with tabs[3]: # CURVA
    st.caption("📈 **Explicación:** Esta curva muestra el ROI de tu tiempo. Si se aplana, considera reducir horas.")
    if st.button("🚀 Calcular Curva"):
        max_h = max(1000, hours_total * 2)
        steps = np.linspace(0, max_h, 30)
        data_curve = []
        pbar = st.progress(0)
        for i, h_sim in enumerate(steps):
            r = run_optimization(df, h_sim, budget=None) 
            data_curve.append({'Horas_Disp': h_sim, 'Valor': r['Score_Real'].sum(), 'Coste_Asociado': r['Coste'].sum()})
            pbar.progress((i+1)/30)
        
        df_curve = pd.DataFrame(data_curve)
        fig_c = px.line(df_curve, x="Horas_Disp", y="Valor", markers=True, title="Curva de Valor vs Dedicación")
        fig_c.add_vline(x=hours_total, line_dash="dash", line_color="red")
        fig_c.add_trace(go.Scatter(x=[hours_total], y=[val], mode='markers+text', marker=dict(color='red', size=15, symbol='star'), text=["TÚ"], name="Plan Actual"))
        st.plotly_chart(fig_c, use_container_width=True)
        
        # RESTAURADO: Diagnóstico Marginal
        st.info(f"""
        **Diagnóstico Inteligente:**
        Con **{hours_total} horas**, consigues **{val:.1f} puntos**.
        
        * **Si la curva sigue subiendo:** Tienes capacidad de absorber más conocimiento valioso.
        * **Si la curva se aplana (Meseta):** Estás entrando en rendimientos decrecientes. Estudiar más horas solo añade actividades de bajo impacto ("relleno").
        """)

with tabs[4]: # AUDITORÍA
    st.caption("🔍 **Explicación:** Datos brutos para verificar por qué el algoritmo tomó sus decisiones.")
    audit_cols = ['ID', 'Actividad', 'Score_Real', 'Probabilidad', 'Probabilidad_Original', 'Eficiencia']
    cols_to_show = [c for c in audit_cols if c in df.columns]
    st.dataframe(df[cols_to_show].sort_values(by='Score_Real', ascending=False), use_container_width=True)

with tabs[5]: # RIESGO
    st.caption("🎲 **Explicación:** Predicción realista. Considera que las tareas suelen retrasarse un 10-50%.")
    if st.button("Lanzar Monte Carlo"):
        mc = run_monte_carlo(df_opt)
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.histogram(mc, x="Horas", title="Distribución de Tiempo Real"), use_container_width=True)
        c2.plotly_chart(px.histogram(mc, x="Valor", title="Distribución de Valor Esperado"), use_container_width=True)
        
        # RESTAURADO: Interpretación de Percentiles
        p50 = np.percentile(mc['Horas'], 50)
        p90 = np.percentile(mc['Horas'], 90)
        st.warning(f"""
        ⚠️ **Análisis de Riesgo:**
        * **Escenario Probable (50%):** Terminarás en **{int(p50)} horas**.
        * **Escenario Pesimista (90%):** Podrías tardar hasta **{int(p90)} horas** si surgen complicaciones técnicas.
        * **Consejo:** Asegúrate de tener un colchón de **{int(p90 - hours_total)} horas** extra disponibles.
        """)

with tabs[6]: # COMPARADOR
    st.caption("🆚 **Explicación:** Usa esto para comparar si es mejor 'Pocos recursos' vs 'Muchos recursos'.")
    if st.session_state['escenarios']:
        cdf = pd.DataFrame(st.session_state['escenarios'])
        st.dataframe(cdf, use_container_width=True)
        st.plotly_chart(px.bar(cdf, x='Nombre', y='Valor', color='Coste'), use_container_width=True)
    else: st.info("Añade escenarios usando el botón 'Comparar' en la barra lateral.")

with tabs[7]: # EXPORTAR
    st.caption("📥 **Explicación:** Descarga y comparte.")
    if not df_opt.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_opt.to_excel(writer, sheet_name='Plan_Optimizado', index=False)
        st.download_button("📥 Descargar Plan (Excel)", buffer.getvalue(), "Plan_SPO.xlsx")