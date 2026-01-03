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
| **Dinero (€)** | Filtro opcional / Output informativo | 72% de actividades son gratuitas o <50€ |

---

## Arquitectura

SPO es un pipeline de inteligencia que separa dos problemas distintos:

```
INTELLIGENCE LAYER (LLM + Web Search)
    Sources: Gartner, McKinsey, Forrester, LangChain, LinkedIn
        |
        v
    Claude Prompt (10 fases)
        - Búsqueda de fuentes (8 queries)
        - Identificación de actividades
        - Detección de sesgos (Hype/Vendor/Survivorship)
        - Red Flags de descarte
        - Clasificación por taxonomía
        - Evaluación con justificación
        - Cálculo de scores
        - Verificación de datos (Horas/Coste desde URL oficial)
        |
        v
    Excel Dataset (12 columnas + URL_Fuente)
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

## Esquema de Datos

El dataset tiene 12 columnas obligatorias:

| Columna | Tipo | Fuente | Descripción |
|---------|------|--------|-------------|
| ID | int | Secuencial | Identificador único |
| Actividad | string | Input | Nombre de la actividad |
| Tipo | string | Clasificación | Formación IA / IA Práctica / Certificación / Visibilidad / Networking |
| Horas | float | URL oficial o web search | Tiempo estimado de dedicación |
| Coste | float | URL oficial o web search | Precio en EUR |
| Pre_req | int | Análisis | ID de prerrequisito (0 si ninguno) |
| Probabilidad | float | Criterio | Probabilidad de completar (0.0-1.0) |
| Capa_id | int | Taxonomía | 1-5 según capa estratégica |
| Capa_desc | string | Taxonomía | Nombre de la capa |
| Capa_score | float | Taxonomía | Puntuación de la capa (5-10) |
| Empleabilidad | float | Web search | Demanda del mercado (1-10) |
| Facilidad | float | Análisis | Facilidad para tu perfil (1-10) |
| URL_Fuente | string | Web search | URL oficial para verificar datos |

---

## Fórmulas

### Score Base (Valor Intrínseco)

```
Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)
```

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

**Decisión:** Horas = restricción principal, Presupuesto = filtro opcional.

**Justificación:** Análisis estadístico mostró que Horas es SIEMPRE binding (100% de escenarios).

### ADR-002: Verificación de Datos desde URL

**Contexto:** El prompt generaba estimaciones de Horas y Coste sin verificar.

**Decisión:** El prompt DEBE buscar Horas y Coste en la URL oficial o fuentes web contrastadas. Si no hay dato verificable, marcar como "VERIFICAR: ~estimación".

**Justificación:** Las estimaciones del LLM diferían de los datos reales de las plataformas.

### ADR-003: IDs Secuenciales

**Contexto:** El prompt asignaba IDs como "NEW1", "NEW2" a actividades nuevas.

**Decisión:** IDs deben ser numéricos secuenciales, continuando desde el máximo del dataset existente.

**Justificación:** Compatibilidad con el sistema de dependencias (Pre_req) y consistencia en el Excel.

### ADR-004: Score Heredado para Gantt

**Decisión:** `Score_Efectivo(task) = max(Score_Real(task), max(Score_Efectivo(hijos)))`

Una tarea pequeña que desbloquea una grande hereda la prioridad de la grande.

---

## Estructura del Repositorio

```
spo/
├── README.md
├── CHANGELOG.md
├── Roadmap_2026.xlsx          # 12 columnas + URL_Fuente
├── app.py
├── data_loader.py
├── engine.py
├── requirements.txt
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

| Componente | Tecnología |
|------------|------------|
| UI | Streamlit |
| Visualización | Plotly |
| Optimización | PuLP (CBC) |
| Data | Pandas |
| LLM | Claude API |

---

## Limitaciones Conocidas

1. Pesos heurísticos (0.4/0.4/0.2) - criterio experto, no validación empírica
2. Monte Carlo simplificado - asume independencia entre tareas
3. Escala del dataset - diseñado para 20-100 actividades
4. Datos marcados "VERIFICAR" requieren validación manual

---

## Licencia

MIT License

---

## Autor

**TU_NOMBRE** - Data & AI Leader

- LinkedIn: linkedin.com/in/TU_PERFIL
- GitHub: github.com/TU_USUARIO
