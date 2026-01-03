# Arquitectura SPO - Strategic Portfolio Optimizer

## Diagrama de Flujo Principal

```mermaid
flowchart TB
    subgraph INTELLIGENCE["🧠 INTELLIGENCE LAYER (LLM + Web Search)"]
        direction TB
        SOURCES["📰 Fuentes<br/>Gartner | McKinsey | Forrester<br/>LangChain | LinkedIn"]
        PROMPT["🤖 Claude Prompt<br/>(9 Fases)"]
        BIAS["🎯 Bias Detection<br/>Hype | Vendor | Survivorship"]
        REDFLAGS["🚩 Red Flags<br/>GitHub < 1K ★<br/>Fuente única<br/>Vendor menor"]
        
        SOURCES --> PROMPT
        PROMPT --> BIAS
        BIAS --> REDFLAGS
    end

    subgraph DATA["📊 DATA LAYER"]
        EXCEL["📁 Excel/CSV<br/>Dataset Estructurado"]
    end

    subgraph COMPUTE["⚙️ COMPUTATION LAYER (Python)"]
        direction TB
        LOADER["data_loader.py<br/>━━━━━━━━━━━<br/>• Score_Base<br/>• Prob_Acumulada<br/>• Score_Real"]
        ENGINE["engine.py<br/>━━━━━━━━━━━<br/>• Knapsack (PuLP)<br/>• Topological Sort<br/>• Monte Carlo"]
        
        LOADER --> ENGINE
    end

    subgraph VIZ["📈 VISUALIZATION LAYER (Streamlit)"]
        direction LR
        SCATTER["Scatter<br/>Valor vs Coste"]
        GANTT["Gantt<br/>Score Heredado"]
        PARETO["Pareto<br/>Frontera"]
        MONTE["Monte Carlo<br/>Riesgo"]
    end

    REDFLAGS --> EXCEL
    EXCEL --> LOADER
    ENGINE --> SCATTER
    ENGINE --> GANTT
    ENGINE --> PARETO
    ENGINE --> MONTE

    style INTELLIGENCE fill:#e1f5fe
    style DATA fill:#fff3e0
    style COMPUTE fill:#f3e5f5
    style VIZ fill:#e8f5e9
```

## Flujo de Cálculo del Score

```mermaid
flowchart LR
    subgraph INPUTS["Inputs"]
        EMP["Empleabilidad<br/>(1-10)"]
        CAPA["Capa_score<br/>(5-10)"]
        FAC["Facilidad<br/>(1-10)"]
        PROB["Probabilidad<br/>(0-1)"]
        DEP["Dependencias<br/>(Pre_req)"]
    end

    subgraph CALC["Cálculos"]
        BASE["Score_Base<br/>━━━━━━━━━━<br/>(Emp×0.4) +<br/>(Capa×0.4) +<br/>(Fac×0.2)"]
        
        ACUM["Prob_Acumulada<br/>━━━━━━━━━━<br/>P × P_padre ×<br/>P_abuelo × ..."]
        
        REAL["Score_Real<br/>━━━━━━━━━━<br/>Base × Acum"]
    end

    subgraph OUTPUT["Output"]
        OPT["🎯 Optimización<br/>Knapsack"]
    end

    EMP --> BASE
    CAPA --> BASE
    FAC --> BASE
    PROB --> ACUM
    DEP --> ACUM
    BASE --> REAL
    ACUM --> REAL
    REAL --> OPT

    style INPUTS fill:#ffecb3
    style CALC fill:#c8e6c9
    style OUTPUT fill:#bbdefb
```

## Taxonomía de Capas

```mermaid
graph TD
    subgraph TAX["Taxonomía Estratégica 2026"]
        L1["🎯 Orchestration<br/>Score: 10<br/>━━━━━━━━━━<br/>LangGraph, MCP<br/>Multi-Agent Systems"]
        L2["🛡️ Governance<br/>Score: 9<br/>━━━━━━━━━━<br/>LangSmith, Evals<br/>AI Safety"]
        L3["💾 Data & Memory<br/>Score: 9<br/>━━━━━━━━━━<br/>RAG, Vector DBs<br/>Embeddings"]
        L4["🤖 Models<br/>Score: 7<br/>━━━━━━━━━━<br/>Prompting, Gemini<br/>Fine-tuning"]
        L5["☁️ Infrastructure<br/>Score: 5<br/>━━━━━━━━━━<br/>Cloud Certs<br/>MLOps"]
    end

    L1 --> L2
    L2 --> L3
    L3 --> L4
    L4 --> L5

    style L1 fill:#4caf50,color:#fff
    style L2 fill:#8bc34a,color:#fff
    style L3 fill:#cddc39
    style L4 fill:#ffeb3b
    style L5 fill:#ff9800
```

## Algoritmo de Gantt (Score Heredado)

```mermaid
flowchart TD
    subgraph LOGIC["Lógica de Priorización"]
        A["Tarea A<br/>Score: 2<br/>Prereq: ninguno"]
        B["Tarea B<br/>Score: 9<br/>Prereq: A"]
        
        A -->|"bloquea"| B
        
        NOTE["💡 A hereda prioridad de B<br/>Score_Efectivo(A) = max(2, 9) = 9<br/><br/>Resultado: A se ejecuta primero<br/>aunque su score propio es bajo"]
    end

    style A fill:#ffcdd2
    style B fill:#c8e6c9
    style NOTE fill:#fff9c4
```

## Detección de Sesgos

```mermaid
flowchart LR
    subgraph BIASES["🎯 Sistema de Detección"]
        H["🔴 HYPE_BIAS<br/>━━━━━━━━━━<br/>• Solo blogs marketing<br/>• Superlativos excesivos<br/>• Sin casos producción<br/><br/>→ Empleabilidad -2"]
        
        V["🟡 VENDOR_BIAS<br/>━━━━━━━━━━<br/>• Solo docs vendor<br/>• Sin validación Gartner<br/>• Sin adopción externa<br/><br/>→ Empleabilidad -1"]
        
        S["🟠 SURVIVORSHIP<br/>━━━━━━━━━━<br/>• Versión 1.x<br/>• Empresa < 2 años<br/>• GitHub < 1K stars<br/><br/>→ DESCARTAR"]
    end

    style H fill:#ffcdd2
    style V fill:#fff9c4
    style S fill:#ffe0b2
```

---

## Stack Tecnológico

| Capa | Tecnología | Rol |
|------|------------|-----|
| Intelligence | Claude API + Web Search | Investigación de tendencias |
| Data | Excel/CSV + Pandas | Almacenamiento estructurado |
| Compute | PuLP (CBC Solver) | Optimización Knapsack |
| Analytics | NumPy | Monte Carlo simulation |
| Visualization | Plotly | Gráficos interactivos |
| UI | Streamlit | Interface web |

---

## Decisiones Arquitectónicas Clave

### ¿Por qué híbrido LLM + Algoritmo?

```
┌─────────────────────────────────────────────────────────────┐
│                    PROBLEMA                                  │
├─────────────────────────────────────────────────────────────┤
│ "¿Qué aprendo para maximizar mi empleabilidad en 2026?"     │
└─────────────────────────────────────────────────────────────┘
                            │
            ┌───────────────┴───────────────┐
            ▼                               ▼
┌───────────────────────┐       ┌───────────────────────┐
│ PARTE NO ESTRUCTURADA │       │ PARTE ESTRUCTURADA    │
├───────────────────────┤       ├───────────────────────┤
│ • ¿Qué tecnologías    │       │ • ¿Cuáles hago        │
│   importan?           │       │   primero?            │
│ • ¿Cuáles tienen      │       │ • ¿Caben en mi        │
│   hype vs realidad?   │       │   presupuesto?        │
│ • ¿Qué dicen los      │       │ • ¿En qué orden       │
│   analistas?          │       │   (dependencias)?     │
├───────────────────────┤       ├───────────────────────┤
│ SOLUCIÓN: LLM         │       │ SOLUCIÓN: Matemáticas │
│ (Claude + Web Search) │       │ (Knapsack + LP)       │
└───────────────────────┘       └───────────────────────┘
```

### Principio de Diseño

> **"LLMs para lo que cambia. Algoritmos para lo que se optimiza."**

El mercado de AI cambia cada mes → LLM lo escanea.
Las restricciones de tiempo/dinero son fijas → Algoritmo las optimiza.
