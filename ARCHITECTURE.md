# SPO Architecture

Documentación técnica de la arquitectura del Strategic Portfolio Optimizer.

---

## 1. Flujo Principal (Time-First)

```mermaid
flowchart TB
    subgraph INTELLIGENCE["Intelligence Layer (LLM)"]
        A[Web Search] --> B[Bias Detection]
        B --> C[Red Flag Filter]
        C --> D[URL Verification]
    end
    
    subgraph DATA["Data Layer"]
        D --> E[Excel: Actividades]
        E --> F[data_loader.py]
        F --> G[Score_Base + Prob_Acum]
    end
    
    subgraph COMPUTE["Compute Layer (Time-First)"]
        G --> H[engine.py]
        H --> I{Restriccion Horas}
        I --> J[Knapsack Optimizer]
        K[Budget Optional] -.-> J
        J --> L[Plan Optimo]
    end
    
    subgraph VIZ["Visualization Layer"]
        L --> M[Streamlit App]
        M --> N[Plan / Gantt / Curva / Risk]
    end
```

---

## 2. Modelo de Datos

```mermaid
erDiagram
    ACTIVIDAD {
        int ID PK
        string Actividad
        string Tipo
        float Horas
        float Coste
        int Pre_req FK
        float Probabilidad
        int Capa_id FK
        string Capa_desc
        float Capa_score
        float Empleabilidad
        float Facilidad
        string URL_Fuente
    }
    
    ACTIVIDAD ||--o| ACTIVIDAD : "depende de"
    
    CAPA {
        int Capa_id PK
        string Capa_desc
        float Capa_score
    }
    
    ACTIVIDAD }|--|| CAPA : "pertenece a"
```

---

## 3. Flujo de Calculo del Score

```mermaid
flowchart LR
    subgraph INPUTS["Inputs (del Excel)"]
        E[Empleabilidad]
        C[Capa_score]
        F[Facilidad]
        P[Probabilidad]
    end
    
    subgraph FORMULA["Formula Ponderada"]
        E -->|x 0.4| SB[Score_Base]
        C -->|x 0.4| SB
        F -->|x 0.2| SB
    end
    
    subgraph CHAIN["Cadena de Dependencias"]
        P --> PA[Prob_Acumulada]
        PA -->|recursivo| PA
    end
    
    subgraph OUTPUT["Output Final"]
        SB --> SR[Score_Real]
        PA --> SR
    end
```

---

## 4. Algoritmo Knapsack (Time-First)

```mermaid
flowchart TB
    START[Dataset + Restricciones] --> CHECK{Budget activado?}
    
    CHECK -->|No| HOURS_ONLY[Solo restriccion Horas]
    CHECK -->|Si| BOTH[Horas + Budget]
    
    HOURS_ONLY --> KNAPSACK[PuLP CBC Solver]
    BOTH --> KNAPSACK
    
    KNAPSACK --> DEP[Verificar Dependencias]
    DEP --> OPTIMAL[Solucion Optima]
    
    OPTIMAL --> OUT_PLAN[Plan Seleccionado]
    OPTIMAL --> OUT_COST[Coste Resultante]
```

---

## 5. Taxonomia de Capas

```mermaid
graph TD
    subgraph STRATEGIC["Alto Valor Estrategico"]
        O[Orchestration: 10]
        G[Governance: 9]
        D[Data and Memory: 9]
    end
    
    subgraph TACTICAL["Valor Tactico"]
        M[Models LLMs: 7]
    end
    
    subgraph FOUNDATIONAL["Foundational"]
        I[Infrastructure: 5]
    end
    
    O --> G
    G --> D
    D --> M
    M --> I
```

---

## 6. Gantt con Score Heredado

```mermaid
flowchart TB
    subgraph PRIORITY["Calculo de Prioridad"]
        A[Tarea A: Score=2] --> B[Tarea B: Score=9]
        B --> C[Tarea C: Score=3]
    end
    
    subgraph EFFECTIVE["Score Efectivo"]
        A2[A hereda 9 de B]
        B2[B mantiene 9]
        C2[C mantiene 3]
    end
    
    subgraph ORDER["Orden de Ejecucion"]
        O1[1. A - desbloquea B]
        O2[2. B - alto valor]
        O3[3. C - bajo valor]
    end
    
    A --> A2
    B --> B2
    C --> C2
    
    A2 --> O1
    B2 --> O2
    C2 --> O3
```

---

## 7. Monte Carlo

```mermaid
flowchart LR
    subgraph SIMULATION["Simulacion N=500"]
        T[Factor Tiempo: U 0.9 1.5]
        S[Exito: Bernoulli P]
    end
    
    subgraph OUTPUTS["Distribuciones"]
        H[Horas Totales]
        V[Valor Total]
    end
    
    subgraph METRICS["Metricas"]
        P50[P50: Escenario Probable]
        P90[P90: Escenario Pesimista]
        P10V[P10 Valor: Suelo Seguro]
    end
    
    T --> H
    S --> V
    H --> P50
    H --> P90
    V --> P10V
```

---

## 8. Componentes del Sistema

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| UI | app.py | Streamlit dashboard, visualizaciones |
| ETL | data_loader.py | Carga Excel, calculo Score_Base, Prob_Acum |
| Optimizer | engine.py | Knapsack, Gantt, Monte Carlo |
| Prompt | AI_Trend_Scanner_v2.2.md | Research + bias detection |
| Data | Roadmap_2026.xlsx | Dataset con URLs |

---

## 9. Principio de Diseno: Hibrido

```mermaid
flowchart LR
    subgraph LLM["LLM No Determinista"]
        R[Research]
        B[Bias Detection]
        E[Empleabilidad]
    end
    
    subgraph ALGO["Algoritmo Determinista"]
        K[Knapsack]
        G[Gantt]
        M[Monte Carlo]
    end
    
    LLM -->|Datos estructurados| ALGO
```

**Principio:** Usar LLMs para lo que son buenos (analisis no estructurado, deteccion de patrones) y algoritmos deterministas para lo que requiere garantias matematicas (optimizacion, scheduling).

---

## 10. Decisiones Tecnicas

| Decision | Alternativa descartada | Razon |
|----------|------------------------|-------|
| PuLP/CBC | Gurobi, CPLEX | Gratuito, suficiente para N<100 |
| Streamlit | Dash, Gradio | Mas rapido para prototipos |
| Excel como fuente | SQLite, Postgres | Portabilidad, edicion manual facil |
| Time-First | Dual constraint | Evidencia estadistica: Horas siempre binding |
