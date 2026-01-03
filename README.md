# SPO: Strategic Portfolio Optimizer

**Un sistema de decisión para carreras en AI que combina LLMs (investigación de mercado) con optimización matemática (priorización de recursos).**

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://portfoliooptimizer-cnzgf5qqsudu95butlxt7r.streamlit.app/)
![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

---

## El Problema

La velocidad del mercado de AI en 2026 genera **parálisis por análisis**: demasiadas tecnologías emergentes (LangGraph, MCP, Agentic RAG...), información sesgada por vendors, y tiempo/presupuesto limitados.

**Pregunta que resuelve SPO:** *"¿Qué debo aprender HOY para maximizar mi empleabilidad como AI Architect, dado mi tiempo y presupuesto?"*

---

## La Solución: Arquitectura Híbrida

SPO no es "una app". Es un **pipeline de inteligencia** que separa dos problemas distintos:

| Problema | Naturaleza | Solución |
|----------|------------|----------|
| *"¿Qué tecnologías importan en 2026?"* | No estructurado, cambiante | LLM + Web Search (Claude) |
| *"¿Cuáles hago primero dado mi presupuesto?"* | Estructurado, determinista | Optimización Matemática (PuLP) |

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        STRATEGIC PORTFOLIO OPTIMIZER                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                    FASE 1: INTELLIGENCE LAYER                        │   │
│  │                        (LLM + Web Search)                            │   │
│  │                                                                      │   │
│  │   ┌──────────┐    ┌──────────────┐    ┌─────────────────────────┐   │   │
│  │   │ Gartner  │───▶│              │───▶│  BIAS DETECTION         │   │   │
│  │   │ McKinsey │    │   Claude     │    │  • Hype Bias            │   │   │
│  │   │ Forrester│    │   Prompt     │    │  • Vendor Bias          │   │   │
│  │   │ LangChain│    │   (9 fases)  │    │  • Survivorship Bias    │   │   │
│  │   │ LinkedIn │    │              │    │                         │   │   │
│  │   └──────────┘    └──────────────┘    └───────────┬─────────────┘   │   │
│  │        ▲                                          │                  │   │
│  │        │              RED FLAGS                   │                  │   │
│  │        │         ┌─────────────────┐              │                  │   │
│  │        └─────────│ • GitHub <1K ★  │◀─────────────┘                  │   │
│  │          DESCARTE│ • Fuente única  │                                 │   │
│  │                  │ • Sin comunidad │                                 │   │
│  │                  └─────────────────┘                                 │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│                         ┌──────────────────┐                                │
│                         │   EXCEL/CSV      │                                │
│                         │   Structured     │                                │
│                         │   Dataset        │                                │
│                         └────────┬─────────┘                                │
│                                  │                                          │
│  ┌───────────────────────────────▼──────────────────────────────────────┐   │
│  │                    FASE 2: COMPUTATION LAYER                          │   │
│  │                         (Python + PuLP)                               │   │
│  │                                                                       │   │
│  │   ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐  │   │
│  │   │  DATA LOADER    │    │    ENGINE       │    │   ANALYTICS     │  │   │
│  │   │                 │    │                 │    │                 │  │   │
│  │   │ • Score_Base    │───▶│ • Knapsack      │───▶│ • Pareto Front  │  │   │
│  │   │ • Prob_Acum     │    │ • Dependencies  │    │ • Monte Carlo   │  │   │
│  │   │ • Score_Real    │    │ • Topological   │    │ • ROI Curves    │  │   │
│  │   │                 │    │   Sort          │    │                 │  │   │
│  │   └─────────────────┘    └─────────────────┘    └─────────────────┘  │   │
│  │                                                                       │   │
│  │   FÓRMULAS:                                                           │   │
│  │   ┌─────────────────────────────────────────────────────────────┐    │   │
│  │   │ Score_Base = (Empleabilidad × 0.4) + (Capa × 0.4) +         │    │   │
│  │   │              (Facilidad × 0.2)                               │    │   │
│  │   │                                                              │    │   │
│  │   │ Prob_Acum = P_propia × P_padre × P_abuelo × ...             │    │   │
│  │   │                                                              │    │   │
│  │   │ Score_Real = Score_Base × Prob_Acum                         │    │   │
│  │   └─────────────────────────────────────────────────────────────┘    │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌───────────────────────────────────────────────────────────────────────┐   │
│  │                    FASE 3: VISUALIZATION LAYER                        │   │
│  │                          (Streamlit + Plotly)                         │   │
│  │                                                                       │   │
│  │   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │   │ Scatter  │  │  Gantt   │  │  Pareto  │  │  Monte   │            │   │
│  │   │ Matrix   │  │ Timeline │  │ Frontier │  │  Carlo   │            │   │
│  │   │          │  │          │  │          │  │          │            │   │
│  │   │ Valor vs │  │ Score    │  │ Retornos │  │ Riesgo   │            │   │
│  │   │ Coste    │  │ Heredado │  │ Decrec.  │  │ Tiempo   │            │   │
│  │   └──────────┘  └──────────┘  └──────────┘  └──────────┘            │   │
│  └───────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Design Decisions (ADRs)

### ADR-001: ¿Por qué Knapsack y no otra heurística?

**Contexto:** Necesitamos seleccionar actividades maximizando valor bajo restricciones de tiempo y dinero.

**Decisión:** Knapsack 0/1 con PuLP (programación lineal entera).

**Alternativas descartadas:**
- *Greedy por ROI:* Ignora dependencias entre actividades
- *Algoritmos genéticos:* Overkill para ~50 items, no determinista
- *Fuerza bruta:* O(2^n) inviable

**Consecuencia:** Solución óptima garantizada en <1s para datasets de hasta 100 actividades.

---

### ADR-002: ¿Por qué separar Score_Base de Score_Real?

**Contexto:** Una actividad puede tener alto valor intrínseco pero depender de 3 prerrequisitos difíciles.

**Decisión:** 
- `Score_Base` = valor intrínseco (Empleabilidad + Capa + Facilidad)
- `Prob_Acumulada` = producto de probabilidades de toda la cadena de dependencias
- `Score_Real` = Score_Base × Prob_Acumulada

**Razonamiento:** Si A depende de B y B depende de C, el valor *real* de A hoy está penalizado por la incertidumbre de completar B y C primero.

---

### ADR-003: ¿Por qué estos pesos (0.4/0.4/0.2)?

**Contexto:** La fórmula pondera tres dimensiones.

| Dimensión | Peso | Justificación |
|-----------|------|---------------|
| Empleabilidad | 40% | Demanda de mercado = proxy de ROI profesional |
| Capa (Taxonomía) | 40% | Alineación con rol objetivo (AI Architect) |
| Facilidad | 20% | Prioriza quick wins sin dominar la decisión |

**Trade-off:** Empleabilidad y Capa tienen igual peso porque un skill muy demandado pero irrelevante para tu rol (ej: DevOps puro) no te acerca al objetivo.

---

### ADR-004: Taxonomía de Capas (¿Por qué Orchestration > Infrastructure?)

**Contexto:** No todas las habilidades tienen el mismo valor estratégico para un AI Architect.

| Capa | Puntuación | Razonamiento |
|------|------------|--------------|
| Orchestration | 10 | Core de sistemas agénticos (LangGraph, MCP) - diferenciador máximo |
| Governance | 9 | Observabilidad, evals, safety - diferenciador enterprise |
| Data & Memory | 9 | RAG, vector DBs - fundamento de aplicaciones LLM |
| Models (LLMs) | 7 | Prompting, fine-tuning - valioso pero commoditizado |
| Infrastructure | 5 | Cloud certs, MLOps - necesario pero no diferenciador |

**Fuente:** Basado en Gartner Strategic Trends 2026 y análisis de job postings.

---

## Estructura del Repositorio

```
spo/
├── app.py                 # UI principal (Streamlit)
├── data_loader.py         # ETL + cálculo de scores
├── engine.py              # Optimización (Knapsack) + Gantt + Monte Carlo
├── requirements.txt       # Dependencias
├── Roadmap_2026.xlsx      # Dataset de actividades
├── prompts/
│   └── AI_Trend_Scanner_v2.1.md   # Prompt de investigación (9 fases)
└── docs/
    └── ARCHITECTURE.md    # Este documento expandido
```

---

## Quick Start

```bash
# Clonar
git clone https://github.com/[tu-usuario]/spo.git
cd spo

# Instalar
pip install -r requirements.txt

# Ejecutar
streamlit run app.py
```

---

## El Prompt de Investigación (AI Trend Scanner)

El dataset no se genera manualmente. Se genera ejecutando un **prompt estructurado de 9 fases** en Claude:

1. **Búsqueda de Fuentes:** 8 queries a Gartner, McKinsey, Forrester, LangChain, LinkedIn
2. **Identificación:** Extracción de skills/herramientas emergentes
3. **Detección de Sesgos:** Evaluación de Hype/Vendor/Survivorship bias
4. **Red Flags:** Descarte automático (GitHub <1K stars, fuente única, vendor menor)
5. **Clasificación:** Asignación a taxonomía de capas
6. **Evaluación:** Scoring justificado con URLs de fuentes
7. **Cálculo:** Score_Real auditable
8. **Output:** Dataset estructurado + comparativa vs roadmap anterior
9. **Validación:** Checklist pre-entrega

**Resultado real (Enero 2026):** El sistema detectó que certificaciones cloud genéricas (DP-203, GCP Professional) han perdido valor frente a skills de producción como LangGraph y MCP Protocol.

---

## Stack Tecnológico

| Componente | Tecnología | Justificación |
|------------|------------|---------------|
| UI | Streamlit | Prototipado rápido, suficiente para MVP |
| Visualización | Plotly | Interactividad necesaria para exploración |
| Optimización | PuLP (CBC) | Solver LP/MIP robusto y gratuito |
| Data | Pandas | Estándar para ETL en Python |
| LLM Layer | Claude API | Capacidad de web search + reasoning |

---

## Limitaciones Conocidas

1. **Datos de entrada:** La calidad del output depende de la ejecución periódica del prompt de investigación
2. **Subjetividad:** Los pesos de la fórmula reflejan prioridades personales (AI Architect)
3. **Escala:** Diseñado para portfolios de 20-100 actividades, no para datasets masivos

---

## Roadmap

- [ ] Pipeline automatizado: Ejecutar prompt de investigación via API
- [ ] Versionado de datasets: Track de cambios en tendencias mes a mes
- [ ] Multi-perfil: Pesos configurables por rol (Data Engineer vs AI Architect)

---

## Licencia

MIT License - Usa, modifica, comparte. Cítame si te es útil.

---

## Autor

**[Tu Nombre]** - Data & AI Leader | Head of Data | AI Architect

[LinkedIn](https://linkedin.com/in/tu-perfil) | [GitHub](https://github.com/tu-usuario)
