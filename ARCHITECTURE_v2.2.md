# SPO Architecture

Documentación técnica de la arquitectura del Strategic Portfolio Optimizer.

---

## 1. Flujo Principal (Time-First + Data Verification)

```mermaid
flowchart TB
    subgraph INTELLIGENCE["Intelligence Layer (LLM)"]
        A[Web Search 8 queries] --> B[Identificar Actividades]
        B --> C[Detectar Sesgos]
        C --> D[Filtrar Red Flags]
        D --> E[Buscar URL oficial]
        E --> F{Horas/Coste en URL?}
        F -->|Si| G[Usar dato verificado]
        F -->|No| H[Marcar VERIFICAR]
    end
    
    subgraph DATA["Data Layer"]
        G --> I[Excel 12 columnas]
        H --> I
        I --> J[data_loader.py]
        J --> K[Score_Base + Prob_Acum]
    end
    
    subgraph COMPUTE["Compute Layer (Time-First)"]
        K --> L[engine.py]
        L --> M{Restriccion Horas}
        M --> N[Knapsack Optimizer]
        O[Budget Optional] -.-> N
        N --> P[Plan Optimo]
    end
    
    subgraph VIZ["Visualization Layer"]
        P --> Q[Streamlit App]
        Q --> R[Plan / Gantt / Curva / Risk]
    end
```

---

## 2. Esquema de Datos (12 columnas)

```mermaid
erDiagram
    ACTIVIDAD {
        int ID PK "Secuencial"
        string Actividad "Nombre"
        string Tipo "Formacion|Practica|Cert|Visibilidad|Networking"
        float Horas "Desde URL o VERIFICAR"
        float Coste "Desde URL o VERIFICAR"
        int Pre_req FK "0 si ninguno"
        float Probabilidad "0.0-1.0"
        int Capa_id FK "1-5"
        string Capa_desc "Nombre capa"
        float Capa_score "5-10"
        float Empleabilidad "1-10 desde web search"
        float Facilidad "1-10 segun perfil"
        string URL_Fuente "URL oficial"
    }
    
    ACTIVIDAD ||--o| ACTIVIDAD : "depende de"
```

---

## 3. Flujo de Verificación de Datos

```mermaid
flowchart LR
    subgraph BUSQUEDA["Búsqueda"]
        A[Actividad identificada] --> B[Buscar URL oficial]
        B --> C[Buscar en plataformas]
        C --> D[Buscar en reviews/blogs]
    end
    
    subgraph DECISION["Decisión"]
        D --> E{Dato encontrado?}
        E -->|URL oficial| F[Usar dato + citar URL]
        E -->|Fuente secundaria| G[Usar dato + citar fuente]
        E -->|No encontrado| H[VERIFICAR: ~estimacion]
    end
    
    subgraph OUTPUT["Output"]
        F --> I[Horas/Coste verificado]
        G --> I
        H --> J[Horas/Coste pendiente]
    end
```

---

## 4. Flujo de Cálculo del Score

```mermaid
flowchart LR
    subgraph INPUTS["Inputs del Excel"]
        E[Empleabilidad 1-10]
        C[Capa_score 5-10]
        F[Facilidad 1-10]
        P[Probabilidad 0-1]
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

## 5. Algoritmo Knapsack (Time-First)

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

## 6. Taxonomía de Capas

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

## 7. Proceso del Prompt (10 Fases)

```mermaid
flowchart TB
    F1[Fase 1: Busqueda de Fuentes] --> F2[Fase 2: Identificacion]
    F2 --> F3[Fase 3: Deteccion Sesgos]
    F3 --> F4[Fase 4: Red Flags]
    F4 --> F5[Fase 5: Clasificacion]
    F5 --> F6[Fase 6: Evaluacion]
    F6 --> F7[Fase 7: Calculo Scores]
    F7 --> F8[Fase 8: Output Estructurado]
    F8 --> F9[Fase 9: Datos Pendientes]
    F9 --> F10[Fase 10: Validacion]
```

---

## 8. Reglas de IDs

```mermaid
flowchart LR
    A[Roadmap existente] --> B[Encontrar max ID]
    B --> C[Nueva actividad]
    C --> D[ID = max + 1]
    D --> E[Siguiente nueva]
    E --> F[ID = max + 2]
    F --> G[...]
```

**Ejemplo:**
- Roadmap actual: IDs 1-18
- Primera actividad nueva: ID 19
- Segunda actividad nueva: ID 20

---

## 9. Componentes del Sistema

| Componente | Archivo | Responsabilidad |
|------------|---------|-----------------|
| UI | app.py | Streamlit dashboard |
| ETL | data_loader.py | Carga Excel, calcula Score_Base, Prob_Acum |
| Optimizer | engine.py | Knapsack, Gantt, Monte Carlo |
| Prompt | AI_Trend_Scanner_v2.2.md | Research + verificacion datos |
| Data | Roadmap_2026.xlsx | Dataset 12 columnas |

---

## 10. Decisiones Técnicas

| Decisión | Alternativa descartada | Razón |
|----------|------------------------|-------|
| PuLP/CBC | Gurobi, CPLEX | Gratuito, suficiente para N<100 |
| Streamlit | Dash, Gradio | Prototipado rápido |
| Excel | SQLite, Postgres | Portabilidad, edición manual |
| Time-First | Dual constraint | Horas siempre binding |
| URL verification | Estimación libre | Precisión de datos |
| IDs secuenciales | IDs tipo "NEW*" | Compatibilidad Pre_req |
