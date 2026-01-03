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

# --- SIDEBAR (CONTROLES REFACTORIZADOS) ---
st.sidebar.header("🕹️ Controles de Estrategia")

# 1. El Slider Maestro (Horas)
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
df_opt = run_optimization(df, hours_total, budget) # Pasamos budget (None o número)
val = df_opt['Score_Real'].sum()
coste_real = df_opt['Coste'].sum()

# --- DASHBOARD (KPIs ACTUALIZADOS) ---
st.title("Strategic Portfolio Optimizer (SPO)")
st.caption(f"Roadmap 2026 | Estrategia basada en Tiempo")

k1, k2, k3, k4 = st.columns(4)
k1.metric("Valor Estratégico", f"{val:.1f}")

# El Tiempo es la restricción (Input vs Usado)
k2.metric("Tiempo Usado", f"{df_opt['Horas'].sum()} h", delta=f"{hours_total - df_opt['Horas'].sum()} h libres")

# El Coste es informativo (Output)
delta_color = "normal" if (budget is None or coste_real <= budget) else "inverse"
presupuesto_str = f"/ {budget}€" if budget else "(Sin límite)"
k3.metric("Coste Resultante", f"{coste_real} €", f"vs {presupuesto_str}")

k4.metric("Actividades", len(df_opt))

tabs = st.tabs(["📖 Contexto", "🎯 Plan", "📅 Gantt", "📈 Curva de Valor", "🔍 Auditoría", "🎲 Riesgo", "🆚 Comparador", "📥 Exportar"])

with tabs[0]: # CONTEXTO
    st.markdown("## 🧠 Manifiesto del Algoritmo (SPO)")
    st.markdown("""
    Bienvenido al **Strategic Portfolio Optimizer**. Esta herramienta no decide por ti, pero **matematiza tu intuición** para maximizar el impacto de tu carrera hacia el perfil de *AI Solutions Architect*.
    """)
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.info("### 1. ¿Qué es el 'Valor Estratégico'?")
        st.markdown("""
        El **KPI Principal (Score Real)** no mide dinero ni horas. Mide **Impacto Profesional**.
        
        Se calcula mediante una **Fórmula Ponderada Ajustada al Riesgo**:
        """)
        st.latex(r'''
        ScoreBase = (Empleabilidad \times 0.4) + (Taxonomía \times 0.4) + (Facilidad \times 0.2)
        ''')
        st.markdown("""
        * **Empleabilidad (40%):** Demanda real del mercado en 2026.
        * **Taxonomía (40%):** Relevancia para el rol de Arquitecto (Orchestration/Governance > Infra).
        * **Facilidad (20%):** Priorización de *Quick Wins*.
        """)
        
        st.markdown("#### 📉 El Ajuste de Realidad")
        st.markdown("El valor final se penaliza por la **Probabilidad Acumulada** de la cadena de dependencias:")
        st.latex(r'''
        ValorReal = ScoreBase \times (P_{propia} \times P_{padre} \times P_{abuelo}...)
        ''')
        st.caption("Una tarea valiosa (10 pts) que depende de 3 tareas difíciles pierde valor real hoy.")

    with c2:
        st.success("### 2. Guía de Interpretación Visual")
        
        with st.expander("🎯 Matriz de Valor (Scatter)", expanded=True):
            st.markdown("""
            * **Eje Y (Alto):** Lo que debes hacer (Alto Valor).
            * **Eje X (Derecha):** Lo que te costará dinero.
            * **Burbujas Verdes:** Seleccionadas por el algoritmo.
            * **Burbujas Rojas:** Descartadas (No caben en presupuesto o tiempo).
            """)
            
        with st.expander("🗺️ Mapa de Calor (Restricciones) - ¡NUEVO!"):
            st.markdown("""
            **Análisis de Sensibilidad (Constraint Landscape).**
            Responde a: *¿Qué me está frenando más: el dinero o el tiempo?*
            * **Movimiento Horizontal (Derecha):** Si añades dinero y el color NO cambia, tienes **holgura financiera**. No gastes más.
            * **Movimiento Vertical (Arriba):** Si añades horas y el color se vuelve amarillo brillante, tu cuello de botella es el **tiempo**.
            """)

        with st.expander("📅 Gantt Inteligente (Back-Propagation)"):
            st.markdown("""
            El cronograma no es lineal. Usa lógica de **Score Heredado**:
            * Si una Tarea A (pequeña) bloquea a una Tarea B (enorme valor), **la Tarea A hereda la prioridad de B**.
            * El algoritmo prioriza los "desbloqueadores" de valor.
            """)
            
        with st.expander("📈 Frontera de Pareto"):
            st.markdown("""
            * **La Curva Azul:** Todo el valor posible que podrías comprar si fueras rico.
            * **La Estrella Roja (TÚ):** Tu posición actual.
            * **Estrategia:** Si estás en la zona empinada, invierte más. Si estás en la zona plana, guarda el dinero (Retornos Decrecientes).
            """)

    st.divider()
    st.markdown("### ⚙️ Taxonomía de Arquitectura 2026")
    st.markdown("Las actividades se clasifican y puntúan según su capa estratégica:")
    
    cols = st.columns(5)
    cols[0].metric("Orchestration", "10 pts", "Core Agéntico")
    cols[1].metric("Governance", "9 pts", "Diferenciador Enterprise")
    cols[2].metric("Data & Memory", "9 pts", "Base del Conocimiento")
    cols[3].metric("Models (LLMs)", "7 pts", "Commodity Potente")
    cols[4].metric("Infrastructure", "5 pts", "Utility")
    
    st.divider()
    st.caption("ℹ️ **Architecture Note:** This system uses a Hybrid AI approach. Unstructured market data is processed by LLMs (Claude 4.5 Opus) to detect bias, while structured optimization is handled by deterministic algorithms (Python/Pulp) to ensure mathematical correctness. See README for ADRs.")

with tabs[1]: # PLAN
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

with tabs[2]: # GANTT
    gantt = calculate_sequential_gantt(df_opt, hours_week)
    if not gantt.empty:
        # Coloreamos por Capa (Taxonomía) para ver la estrategia visualmente
        color_col = 'Capa_desc' if 'Capa_desc' in gantt.columns else 'Tipo'
        fig_g = px.timeline(gantt, x_start="Inicio", x_end="Fin", y="Tarea", color=color_col, hover_data=['Pre_req', 'Prioridad_Calc'])
        fig_g.update_yaxes(autorange="reversed")
        st.plotly_chart(fig_g, use_container_width=True)
        st.success(f"📅 Fin Estimado: **{gantt['Fin'].max().strftime('%d/%m/%Y')}**")
    else: st.info("Sin tareas seleccionadas.")

with tabs[3]: # CURVA DE VALOR (Sustituye a Frontera y Mapa Calor)
    st.markdown("### 📈 Análisis de Sensibilidad Temporal")
    st.markdown("Esta curva responde a: **¿Cuánto valor gano si dedico más horas?** (Diminishing Returns del Tiempo)")
    
    if st.button("🚀 Calcular Curva"):
        # Simulamos rangos de Horas (de 0 a 1.5 veces tu disponibilidad actual)
        # Asumimos presupuesto infinito para ver el potencial puro del tiempo
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
        
        # Tu posición
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
        
        * **Si la curva sigue subiendo:** Tienes capacidad de absorber más conocimiento si sacas tiempo.
        * **Si la curva se aplana:** Estás saturado. Estudiar más horas no te dará mejores skills (ya has cogido todo lo bueno).
        """)
            
with tabs[4]: # AUDITORÍA (ACTUALIZADA)
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

with tabs[5]: # RIESGO
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
        st.download_button("📥 Descargar Plan", buffer.getvalue(), "Plan_SPO.xlsx")












