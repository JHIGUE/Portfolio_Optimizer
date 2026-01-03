# SPO: Strategic Portfolio Optimizer

Sistema de decisión para carreras en AI que combina LLMs (investigación de mercado) con optimización matemática (priorización de recursos).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://portfoliooptimizer-cnzgf5qqsudu95butlxt7r.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## El Problema

El mercado de AI en 2026 genera parálisis por análisis: demasiadas tecnologías emergentes, información sesgada por vendors, tiempo y presupuesto limitados.

**Pregunta que resuelve SPO:** "¿Qué debo aprender HOY para maximizar mi empleabilidad como AI Architect, dado mi tiempo y presupuesto?"

---

## Arquitectura

SPO es un pipeline de inteligencia que separa dos problemas distintos:

| Problema | Naturaleza | Solución |
|----------|------------|----------|
| "¿Qué tecnologías importan en 2026?" | No estructurado, cambiante | LLM + Web Search |
| "¿Cuáles hago primero dado mi presupuesto?" | Estructurado, determinista | Optimización Matemática (PuLP) |

```
INTELLIGENCE LAYER (LLM + Web Search)
    Sources (Gartner, McKinsey, Forrester, LangChain, LinkedIn)
        |
        v
    Claude Prompt (9 phases) --> Bias Detection --> Red Flag Filter
                                (Hype/Vendor/     (GitHub <1K,
                                 Survivorship)     Single source)
        |
        v
    Excel Dataset (Empleabilidad, Facilidad, Capa, Probabilidad)
        |
        v
COMPUTATION LAYER (Python)
    data_loader.py        engine.py              Analytics
    - Score_Base          - Knapsack (PuLP)      - Pareto Frontier
    - Prob_Acumulada      - Topological Sort     - Monte Carlo
    - Score_Real          - Gantt Scheduling     - ROI Analysis
        |
        v
VISUALIZATION LAYER (Streamlit + Plotly)
    Scatter | Gantt | Efficiency Curve | Risk Simulation
```

---

## Fórmulas

### Score Base (Valor Intrínseco)

```
Score_Base = (Empleabilidad × 0.4) + (Capa_score × 0.4) + (Facilidad × 0.2)
```

| Componente | Peso | Descripción |
|------------|------|-------------|
| Empleabilidad | 40% | Demanda real del mercado (1-10) |
| Capa_score | 40% | Valor estratégico según taxonomía (5-10) |
| Facilidad | 20% | Inverso de dificultad, prioriza quick wins (1-10) |

### Score Real (Ajustado por Riesgo)

```
Prob_Acumulada = P_propia × P_padre × P_abuelo × ...
Score_Real = Score_Base × Prob_Acumulada
```

Una tarea valiosa que depende de prerrequisitos difíciles tiene menor valor real HOY.

---

## Taxonomía de Capas

| Capa | Puntuación | Razonamiento |
|------|------------|--------------|
| Orchestration | 10 | Core de sistemas agénticos (LangGraph, MCP) |
| Governance | 9 | Observabilidad, evals, safety (LangSmith) |
| Data & Memory | 9 | RAG, vector DBs, embeddings |
| Models | 7 | Prompting, fine-tuning (commoditizado) |
| Infrastructure | 5 | Cloud certs, MLOps (necesario pero no diferenciador) |

Basado en Gartner Strategic Trends 2026 y análisis de job postings.

---

## Design Decisions (ADRs)

### ADR-001: Por qué Knapsack

**Problema:** Seleccionar actividades maximizando valor bajo restricciones.

**Decisión:** Knapsack 0/1 con PuLP (programación lineal entera).

**Alternativas descartadas:**
- Greedy por ROI: Ignora dependencias
- Algoritmos genéticos: Overkill para N~50, no determinista
- Fuerza bruta: O(2^n) inviable

### ADR-002: Por qué separar Score_Base de Score_Real

Si A depende de B y B depende de C, el valor de A hoy está penalizado por la incertidumbre de completar B y C primero. Score_Real captura esto.

### ADR-003: Por qué estos pesos (0.4/0.4/0.2)

Empleabilidad y Capa tienen igual peso porque un skill muy demandado pero irrelevante para el rol objetivo no acerca a la meta. Facilidad tiene menor peso para evitar que dominen los quick wins triviales.

---

## Algoritmos Implementados

### 1. Knapsack Multidimensional

```python
Maximizar: Σ Score_Real[i] × x[i]
Sujeto a:
  Σ Coste[i] × x[i] ≤ Presupuesto
  Σ Horas[i] × x[i] ≤ Horas_disponibles
  x[hijo] ≤ x[padre]  # Dependencias
  x[i] ∈ {0, 1}
```

### 2. Gantt con Score Heredado

```python
Score_Efectivo(task) = max(Score_Real(task), max(Score_Efectivo(hijos)))
```

Una tarea pequeña que desbloquea una grande hereda la prioridad de la grande. Prioriza "desbloqueadores de valor".

### 3. Monte Carlo

Simula incertidumbre en:
- Tiempo: Factor U(0.9, 1.5) sobre estimaciones
- Completación: Bernoulli con probabilidad de cada tarea

Genera distribuciones de horas totales y valor esperado.

---

## Estructura del Repositorio

```
spo/
├── app.py                 # UI principal (Streamlit)
├── data_loader.py         # ETL + cálculo de scores
├── engine.py              # Optimización + Gantt + Monte Carlo
├── requirements.txt
├── Roadmap_2026.xlsx      # Dataset con Empleabilidad, Facilidad, Capa, etc.
├── LICENSE
├── prompts/
│   └── AI_Trend_Scanner_v2.1.md
├── tests/
│   └── test_engine.py
└── docs/
    ├── ARCHITECTURE.md
    └── STATISTICAL_AUDIT.md
```

---

## Quick Start

```bash
git clone https://github.com/TU_USUARIO/spo.git
cd spo
pip install -r requirements.txt
streamlit run app.py
```

---

## Stack Tecnológico

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| UI | Streamlit | Prototipado rápido |
| Visualización | Plotly | Interactividad |
| Optimización | PuLP (CBC) | Solver LP/MIP robusto, gratuito |
| Data | Pandas | ETL estándar |
| LLM | Claude API | Web search + reasoning para research |

---

## Limitaciones Conocidas

1. **Pesos heurísticos:** 0.4/0.4/0.2 elegidos por criterio experto, no validación empírica
2. **Monte Carlo simplificado:** Asume independencia entre tareas (las dependencias no propagan fallos)
3. **Escala del dataset:** Diseñado para 20-100 actividades
4. **Sin back-testing:** No hay validación contra resultados reales de carrera

---

## Validación Estadística

Ver `docs/STATISTICAL_AUDIT.md` para análisis completo que incluye:
- Evaluación de fórmulas y pesos
- Análisis del algoritmo Knapsack
- Crítica del Monte Carlo
- Comparativa con herramientas similares (Jira Portfolio, ProductBoard, RICE)

---

## Licencia

MIT License

---

## Autor

Javier Higuera - Data & AI Leader

- LinkedIn: www.linkedin.com/in/javier-higuera-porteros
- GitHub: https://github.com/JHIGUE
