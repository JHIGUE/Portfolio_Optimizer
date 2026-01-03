# SPO: Strategic Portfolio Optimizer

Sistema de decisión para carreras en AI que combina LLMs (investigación de mercado) con optimización matemática (priorización de recursos).

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://portfoliooptimizer-cnzgf5qqsudu95butlxt7r.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## El Problema

El mercado de AI en 2026 genera parálisis por análisis: demasiadas tecnologías emergentes, información sesgada por vendors, tiempo limitado.

**Pregunta que resuelve SPO:** "¿Qué debo aprender HOY para maximizar mi empleabilidad como AI Architect, dado mi tiempo disponible?"

---

## Filosofía: Time-First

La versión 2.2 adopta un modelo **Time-First** basado en evidencia empírica:

| Recurso | Rol en el modelo | Justificación |
|---------|------------------|---------------|
| **Tiempo (Horas)** | Restricción principal | Siempre es el cuello de botella real |
| **Dinero (€)** | Filtro opcional / Output informativo | 72% de actividades son gratuitas o <€50 |

En el análisis estadístico, la correlación Horas-Coste es r=0.93 (casi redundantes) y las Horas son binding en el 100% de los escenarios probados. El modelo anterior con dos restricciones iguales confundía al usuario.

---

## Arquitectura

SPO es un pipeline de inteligencia que separa dos problemas distintos:

```
INTELLIGENCE LAYER (LLM + Web Search)
    Sources: Gartner, McKinsey, Forrester, LangChain, LinkedIn
        |
        v
    Claude Prompt (9 phases)
        - Bias Detection (Hype/Vendor/Survivorship)
        - Red Flag Filter (GitHub <1K, Single source)
        - URL Verification (Horas y Coste de fuentes oficiales)
        |
        v
    Excel Dataset
        |
        v
COMPUTATION LAYER (Python)
    data_loader.py              engine.py
    - Score_Base                - Knapsack (Horas = restricción principal)
    - Prob_Acumulada            - Budget = opcional
    - Score_Real                - Gantt con Score Heredado
        |
        v
VISUALIZATION LAYER (Streamlit + Plotly)
    Plan | Gantt | Curva de Valor | Monte Carlo
```

---

## Fórmulas

### Score Base (Valor Intrínseco)

```
Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)
```

| Componente | Peso | Descripción |
|------------|------|-------------|
| Empleabilidad | 40% | Demanda real del mercado (1-10) |
| Capa_score | 40% | Valor estratégico según taxonomía (5-10) |
| Facilidad | 20% | Inverso de dificultad, prioriza quick wins (1-10) |

### Score Real (Ajustado por Riesgo)

```
Prob_Acumulada = P_propia * P_padre * P_abuelo * ...
Score_Real = Score_Base * Prob_Acumulada
```

### Optimización (Time-First)

```
Maximizar: Sum(Score_Real[i] * x[i])
Sujeto a:
  Sum(Horas[i] * x[i]) <= Horas_disponibles    # SIEMPRE ACTIVA
  Sum(Coste[i] * x[i]) <= Presupuesto          # SOLO SI SE ACTIVA
  x[hijo] <= x[padre]                          # Dependencias
  x[i] in {0, 1}
```

---

## Taxonomía de Capas

| Capa | Puntuación | Razonamiento |
|------|------------|--------------|
| Orchestration | 10 | Core de sistemas agénticos (LangGraph, MCP) |
| Governance | 9 | Observabilidad, evals, safety (LangSmith) |
| Data & Memory | 9 | RAG, vector DBs, embeddings |
| Models | 7 | Prompting, fine-tuning (commoditizado) |
| Infrastructure | 5 | Cloud certs, MLOps (necesario pero no diferenciador) |

---

## Design Decisions (ADRs)

### ADR-001: Time-First Model

**Contexto:** El modelo original trataba Horas y Presupuesto como restricciones iguales.

**Problema:** Análisis estadístico reveló que Horas es SIEMPRE la restricción binding (100% de escenarios). El presupuesto nunca limitaba las decisiones.

**Decisión:** 
- Horas = restricción principal (siempre activa)
- Presupuesto = filtro opcional (desactivado por defecto)
- Coste = output informativo ("esto es lo que cuesta tu plan")

**Consecuencias:** UI más simple, modelo mental más honesto.

### ADR-002: URL Verification para Horas y Coste

**Contexto:** El prompt de AI Trend Scanner generaba estimaciones de Horas y Coste.

**Problema:** Las estimaciones diferían de los datos reales de las plataformas.

**Decisión:** El prompt DEBE extraer Horas y Coste de la URL oficial, no estimarlos. Actividades sin datos verificados se marcan como "VERIFICAR".

### ADR-003: Score Heredado para Gantt

**Contexto:** Tareas pequeñas pueden bloquear tareas de alto valor.

**Decisión:** `Score_Efectivo(task) = max(Score_Real(task), max(Score_Efectivo(hijos)))`

Una tarea pequeña que desbloquea una grande hereda la prioridad de la grande.

---

## Estructura del Repositorio

```
spo/
├── app.py                 # UI principal (Streamlit)
├── data_loader.py         # ETL + cálculo de scores
├── engine.py              # Optimización Time-First + Gantt
├── requirements.txt
├── Roadmap_2026.xlsx      # Dataset con URL_Fuente
├── LICENSE
├── prompts/
│   └── AI_Trend_Scanner_v2.2.md
├── tests/
│   └── test_engine.py
└── docs/
    ├── ARCHITECTURE.md
    ├── STATISTICAL_AUDIT.md
    └── EXECUTIVE_SUMMARY.md
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
2. **Monte Carlo simplificado:** Asume independencia entre tareas
3. **Escala del dataset:** Diseñado para 20-100 actividades
4. **Sin back-testing:** No hay validación contra resultados reales de carrera

---

## Validación Estadística

Ver `docs/STATISTICAL_AUDIT.md` para análisis completo:
- Puntuación: 8.15/10
- Ranking estable (Spearman >0.93) ante cambios de pesos
- Tiempo SIEMPRE binding, nunca presupuesto

---

## Changelog

Ver `CHANGELOG.md` para historial completo.

**v2.2.0 (2026-01-03):** Time-First Model, URL verification, Curva de Valor

---

## Licencia

MIT License

---

## Autor

Javier Higuera Porteros - Data & AI Leader

- LinkedIn: https://linkedin.com/in/javier-higuera-porteros
- GitHub: https://github.com/JHIGUE
