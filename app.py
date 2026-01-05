import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go # IMPORTANTE: Necesario para las estrellas y líneas rojas
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
    # Nota: Guardamos budget aunque sea None para el historial
    b_val = budget if budget is not None else "Ilimitado"
    df_new = pd.DataFrame([{'Fecha': ts, 'Escenario': name, 'Presupuesto': b_val, 'Horas': hours, 'Valor': score, 'Coste': cost, 'Tiempo_Real': time, 'Items': items}])
    if not os.path.exists(HISTORY_FILE): df_new.to_csv(HISTORY_FILE, index=False)
    else: df_new.to_csv(HISTORY_FILE, mode='a', header=False, index=False)

# --- CARGA DE DATOS ---
# Usamos rutas relativas/absolutas seguras
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

# --- SIDEBAR (CONTROLES REFACTORIZADOS TIME-FIRST) ---
st.sidebar.header("🕹️ Controles de Estrategia")

# 1. El Slider Maestro (Horas) - Ahora es el protagonista
hours_total = st.sidebar.slider("⏳ Tu Tiempo (Bolsa Horas Anual)", 0, 1000, 300, step=10)
hours_week = st.sidebar.number_input("Velocidad (Horas/Semana)", 1, 40, 10)

st.sidebar.divider()

# 2. La Restricción Opcional (Presupuesto)
use_budget = st.sidebar.checkbox("🔒 Activar límite de Presupuesto", value=False)

if use_budget:
    budget = st.sidebar.slider("💰 Presupuesto Máximo (€)", 0, 5000, 600, step=50)
else:
    budget = None # Señal para el motor de que no hay límite
    st.sidebar.caption("✅ Presupuesto ilimitado (El coste será un resultado, no un límite).")

st.sidebar.divider()

# 3. Gestión de Escenarios
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
# Llamamos a engine con la nueva lógica (horas obligatorias, budget opcional)
df_opt = run_optimization(df, hours_total, budget)
val = df_opt['Score_Real'].sum()
coste_real = df_opt['Coste'].sum()

# --- DASHBOARD (KPIs NUEVOS) ---
st.title("Strategic Portfolio Optimizer (SPO)")
st.caption(f"Roadmap 2026 | Estrategia 'Time-First' (Prioridad al Tiempo)")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Valor Estratégico", f"{val:.1f}")

# El Tiempo es la restricción (Input vs Usado)
k2.metric("Tiempo Usado", f"{df_opt['Horas'].sum()} h", delta=f"{hours_total - df_opt['Horas'].sum()} h libres")

# El Coste es informativo (Output)
delta_color = "normal" if (budget is None or coste_real <= budget) else "inverse"
presupuesto_str = f"/ {budget}€" if budget else "(Sin límite)"
k3.metric("Coste Resultante", f"{coste_real} €", f"vs {presupuesto_str}")

k4.metric("Actividades", len(df_opt))

# --- PESTAÑAS (ESTRUCTURA NUEVA) ---
tabs = st.tabs(["📖 Contexto", "🎯 Plan", "📅 Gantt", "📈 Curva de Valor", "🔍 Auditoría", "🎲 Riesgo", "🆚 Comparador", "📥 Exportar"])

with tabs[0]: # CONTEXTO (ACTUALIZADO A LA NUEVA REALIDAD)
    st.markdown("## 🧠 Manifiesto del Algoritmo (SPO) - Time-First Edition")
    st.markdown("""
    **La realidad de 2026:** El conocimiento de IA es abundante y barato (Open Source). Tu verdadera restricción no es el dinero, es tu **capacidad cognitiva y tu tiempo**.
    """)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("### 1. La Lógica del Motor")
        st.markdown("""
        Hemos refactorizado el optimizador para reflejar la realidad del mercado:
        
        * **⏳ Input Principal (El Cuello de Botella):** Tus horas disponibles. El algoritmo busca el máximo impacto que cabe en tu agenda.
        * **💰 Input Secundario (El Filtro):** El presupuesto es opcional. Solo actúa como un "freno" si decides activarlo.
        * **💎 Output (El Objetivo):** Maximizar el **Valor Estratégico (Score Real)**.
        """)
        
        st.markdown("#### 📐 La Fórmula del Valor")
        st.latex(r'''
        ScoreBase = (Empleabilidad \times 0.4) + (Taxonomía \times 0.4) + (Facilidad \times 0.2)
        ''')
        st.caption("Ponderamos qué pide el mercado, qué te posiciona como Arquitecto y qué puedes aprender rápido.")

    with c2:
        st.success("### 2. Guía de Interpretación Visual")
        
        with st.expander("📈 Curva de Valor (Sensibilidad Temporal) - ¡NUEVO!"):
            st.markdown("""
            **Responde a:** *¿Merece la pena estudiar más horas?*
            * **Curva Empinada:** Estás aprendiendo skills críticos. Cada hora extra vale oro.
            * **Curva Plana (Meseta):** Rendimientos decrecientes. Estudiar más horas solo añade valor marginal (skills de relleno).
            * **Tu Posición (Línea Roja):** Te dice si te has quedado corto o si te estás pasando de frenada.
            """)

        with st.expander("📅 Gantt Topológico (Back-Propagation)"):
            st.markdown("""
            El orden no es casual. Si una tarea pequeña desbloquea a una grande, el algoritmo la pone primero.
            * **Color:** Indica la Capa Estratégica (Orquestación, Datos, Gobierno...).
            """)
            
        with st.expander("🎯 Matriz de Valor (Scatter)"):
            st.markdown("""
            * **Eje Y:** Impacto Profesional (Score Real).
            * **Eje X:** Esfuerzo en Horas.
            * **Burbujas Verdes:** Entran en tu agenda.
            """)

    st.divider()
    st.markdown("### ⚙️ Taxonomía de Arquitectura 2026")
    
    cols = st.columns(5)
    cols[0].metric("Orchestration", "10 pts", "Core Agéntico")
    cols[1].metric("Governance", "9 pts", "Diferenciador Enterprise")
    cols[2].metric("Data & Memory", "9 pts", "Base del Conocimiento")
    cols[3].metric("Models (LLMs)", "7 pts", "Commodity Potente")
    cols[4].metric("Infrastructure", "5 pts", "Utility")
    
    st.divider()
    st.caption("ℹ️ **Architecture Note:** Hybrid AI System. Unstructured trend analysis via LLMs (Claude) + Deterministic Optimization via Python (Pulp). See README for Architecture Decision Records (ADRs).")

with tabs[1]: # PLAN (ACTUALIZADO: EJE X = HORAS)
    c1, c2 = st.columns([2,1])
    with c1:
        # Estado para colorear
        df['Estado'] = np.where(df.index.isin(df_opt.index), 'SI', 'NO')
        
        # SCATTER: Eje X es Horas. Tamaño es Horas.
        fig = px.scatter(df, 
                         x="Horas", 
                         y="Score_Real", 
                         color="Estado", 
                         size="Horas", # Burbuja proporcional al tiempo
                         hover_data=['Actividad', 'Coste', 'Probabilidad', 'Capa_desc'], 
                         color_discrete_map={'SI':'#00CC96', 'NO':'#EF553B'},
                         title="Matriz Valor (Y) vs Esfuerzo en Horas (X)")
        
        fig.update_layout(xaxis_title="Horas de Dedicación", yaxis_title="Score Real (Valor)")
        st.plotly_chart(fig, use_container_width=True)
        
    with c2:
        st.subheader("Selección por Eficiencia")
        # Tabla muestra HORAS en vez de coste
        st.dataframe(
            df_opt[['Actividad', 'Horas', 'Eficiencia']]
            .sort_values(by='Eficiencia', ascending=False), 
            hide_index=True
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

with tabs[3]: # CURVA DE VALOR (NUEVA: SENSIBILIDAD TEMPORAL)
    st.markdown("### 📈 Análisis de Sensibilidad Temporal")
    st.markdown("Esta curva responde a: **¿Cuánto valor gano si dedico más horas?** (Diminishing Returns del Tiempo)")
    
    if st.button("🚀 Calcular Curva"):
        # Simulamos rangos de Horas (de 0 a 2 veces tu disponibilidad actual)
        # Asumimos presupuesto infinito (budget=None) para ver el potencial puro del tiempo
        max_h = max(1000, hours_total * 2)
        steps = np.linspace(0, max_h, 30)
        
        data_curve = []
        pbar = st.progress(0)
        
        for i, h_sim in enumerate(steps):
            # Optimizamos variando horas, SIN límite de presupuesto (budget=None)
            r = run_optimization(df, h_sim, budget=None) 
            data_curve.append({
                'Horas_Disp': h_sim, 
                'Valor': r['Score_Real'].sum(),
                'Coste_Asociado': r['Coste'].sum() # Informativo
            })
            pbar.progress((i+1)/30)
            
        df_curve = pd.DataFrame(data_curve)
        
        # Gráfico
        fig_c = px.line(df_curve, x="Horas_Disp", y="Valor", markers=True,
                        title="Curva de Valor vs Dedicación",
                        labels={"Horas_Disp": "Horas Invertidas", "Valor": "Impacto Profesional"})
        
        # Tu posición (Línea Vertical + Estrella)
        fig_c.add_vline(x=hours_total, line_dash="dash", line_color="red", annotation_text="Tu Tiempo Actual")
        fig_c.add_trace(go.Scatter(
            x=[hours_total], y=[val], mode='markers+text', 
            marker=dict(color='red', size=15, symbol='star'),
            text=["TÚ"], textposition="top left", name="Plan Actual"
        ))
        
        st.plotly_chart(fig_c, use_container_width=True)
        
        # Diagnóstico Marginal
        st.info(f"""
        **Diagnóstico:**
        Con **{hours_total} horas**, consigues **{val:.1f} puntos**.
        El coste asociado a este plan de tiempo es de **{coste_real}€**.
        
        * **Si la curva sigue subiendo:** Tienes capacidad de absorber más conocimiento si sacas tiempo de donde sea.
        * **Si la curva se aplana:** Estás saturado. Estudiar más horas no te dará mejores skills (ya has cogido todo lo bueno).
        """)

with tabs[4]: # AUDITORÍA
    # Mostramos columnas clave nuevas
    audit_cols = ['ID', 'Actividad', 'Capa_desc', 'Empleabilidad', 'Facilidad', 'Score_Real', 'Probabilidad_Acumulada']
    cols_to_show = [c for c in audit_cols if c in df.columns]
    st.dataframe(df[cols_to_show].sort_values(by='Score_Real', ascending=False), use_container_width=True)

with tabs[5]: # RIESGO
    if st.button("Lanzar Monte Carlo"):
        mc = run_monte_carlo(df_opt)
        
        c1, c2 = st.columns(2)
        c1.plotly_chart(px.histogram(mc, x="Horas", title="Distribución de Tiempo Real"), use_container_width=True)
        c2.plotly_chart(px.histogram(mc, x="Valor", title="Distribución de Valor Esperado"), use_container_width=True)
        
        # Interpretación
        p50 = np.percentile(mc['Horas'], 50)
        p90 = np.percentile(mc['Horas'], 90)
        st.info(f"📅 **Predicción:** Es probable (50%) que termines en **{int(p50)}h**, pero prepárate para **{int(p90)}h** en el peor caso.")

with tabs[6]: # COMPARADOR
    if st.session_state['escenarios']:
        cdf = pd.DataFrame(st.session_state['escenarios'])
        st.dataframe(cdf, use_container_width=True)
        st.plotly_chart(px.bar(cdf, x='Nombre', y='Valor', color='Coste'), use_container_width=True)
    else: st.info("Añade escenarios para comparar.")

with tabs[7]: # EXPORTAR
    if not df_opt.empty:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df_opt.to_excel(writer, sheet_name='Plan_Optimizado', index=False)
        st.download_button("📥 Descargar Plan (Excel)", buffer.getvalue(), "Plan_SPO.xlsx")