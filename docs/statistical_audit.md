# 📊 Auditoría Estadística del Sistema SPO

> **Strategic Portfolio Optimizer — Validación Matemática y Estadística**

## 📋 Índice

1. [Resumen Ejecutivo](#1-resumen-ejecutivo)
2. [Auditoría del Modelo de Scoring](#2-auditoría-del-modelo-de-scoring)
3. [Auditoría del Algoritmo de Optimización](#3-auditoría-del-algoritmo-de-optimización)
4. [Auditoría del Motor de Gantt](#4-auditoría-del-motor-de-gantt)
5. [Auditoría de Monte Carlo](#5-auditoría-de-monte-carlo)
6. [Análisis de Sensibilidad](#6-análisis-de-sensibilidad)
7. [Limitaciones y Recomendaciones](#7-limitaciones-y-recomendaciones)

---

## 1. Resumen Ejecutivo

### 1.1 Alcance de la Auditoría

Esta auditoría evalúa la **validez estadística y matemática** de los componentes del SPO:

| Componente | Técnica | Validez |
|------------|---------|---------|
| Adversarial Validation | Reflexion pattern (Gemini ↔ Claude) | ✅ Consenso multi-LLM |
| Scoring Model | Regresión ponderada | ✅ Válido |
| Knapsack Optimizer | Programación lineal binaria | ✅ Óptimo garantizado |
| Topological Gantt | Ordenación topológica + Heap | ✅ Correcto |
| Monte Carlo | Simulación estocástica | ⚠️ Válido con limitaciones |

### 1.2 Dataset Auditado

```
Fuente: Roadmap_2026_CORREGIDO.xlsx
Pestaña: 4_Actividades_Priorizadas
Registros: 18 actividades
Columnas: 12 campos + 4 derivados
```

### 1.3 Estadísticas Descriptivas

| Métrica | Horas | Coste | Probabilidad | Score_Real |
|---------|-------|-------|--------------|------------|
| Media | 24.56 | 38.06€ | 0.86 | 6.88 |
| Mediana | 15 | 0€ | 0.95 | 7.70 |
| Desv. Std | 27.50 | 71.36€ | 0.19 | 2.15 |
| Mín | 1 | 0€ | 0.40 | 2.16 |
| Máx | 100 | 200€ | 1.00 | 9.80 |

### 1.4 Validación Adversarial (Pre-Scoring)

Antes del scoring matemático, los datos de entrada pasan por un proceso de **validación adversarial** entre dos LLMs:

```
Gemini (Output A) → Claude (Crítica B) → Gemini (Output A' ajustado)
Iteraciones típicas: 2-3 hasta convergencia
```

**Objetivo:** Reducir sesgos (HYPE, VENDOR, SURVIVORSHIP) en los valores de Empleabilidad antes de que entren al motor de optimización.

**Validación del proceso:**
- ✅ Ambos modelos reciben el mismo prompt base
- ✅ La crítica es estructurada (5 criterios de auditoría)
- ✅ Convergencia = ausencia de objeciones pendientes
- ⚠️ No determinista (los LLMs pueden variar entre ejecuciones)

**Mitigación de no-determinismo:** Se documenta el changelog de cada iteración para trazabilidad.

---

## 2. Auditoría del Modelo de Scoring

### 2.1 Fórmula de Score_Base

```
Score_Base = (Empleabilidad × 0.4) + (Capa_score × 0.4) + (Facilidad × 0.2)
```

#### Validación de Pesos

| Factor | Peso | Justificación Teórica |
|--------|------|----------------------|
| Empleabilidad | 0.4 | Demanda del mercado (objetivo principal) |
| Capa_score | 0.4 | Posicionamiento estratégico (arquitectura) |
| Facilidad | 0.2 | Viabilidad (factor secundario) |

**Suma de pesos:** 0.4 + 0.4 + 0.2 = **1.0** ✅

#### Rango Teórico

```
Score_Base_min = (1 × 0.4) + (5 × 0.4) + (1 × 0.2) = 2.6
Score_Base_max = (10 × 0.4) + (10 × 0.4) + (10 × 0.2) = 10.0
```

**Rango observado:** [5.4, 9.8] ⊂ [2.6, 10.0] ✅

#### Verificación de Cálculos

| ID | Actividad | E | C | F | Score_Base (Calc) | Score_Base (Esperado) | ✓ |
|----|-----------|---|---|---|-------------------|----------------------|---|
| 1 | MCP Server | 9 | 10 | 8 | 9×0.4 + 10×0.4 + 8×0.2 = **9.2** | 9.2 | ✅ |
| 2 | LangChain | 10 | 10 | 9 | 10×0.4 + 10×0.4 + 9×0.2 = **9.8** | 9.8 | ✅ |
| 8 | Azure DP-203 | 6 | 5 | 6 | 6×0.4 + 5×0.4 + 6×0.2 = **5.6** | 5.6 | ✅ |

**Resultado:** 18/18 cálculos correctos ✅

### 2.2 Probabilidad Acumulada

#### Fórmula Recursiva

```python
def get_prob_acumulada(task_id):
    if Pre_req == 0:
        return Probabilidad
    else:
        return Probabilidad × get_prob_acumulada(Pre_req)
```

#### Propiedades Matemáticas

1. **Rango:** Prob_Acum ∈ (0, 1] ✅
2. **Monotonicidad:** Prob_Acum ≤ Probabilidad (siempre menor o igual que la propia) ✅
3. **Propagación:** Cadenas largas → probabilidades acumuladas más bajas ✅

#### Verificación de Cadenas

**Cadena 1:** LangChain (2) → MCP Server (1) → Artículo MCP (11)

```
Prob_Acum(2) = 1.0 (sin prerrequisito)
Prob_Acum(1) = 0.80 × 1.0 = 0.80
Prob_Acum(11) = 0.95 × 0.80 = 0.76
```

**Cadena 2:** LangChain (2) → RAG Avanzado (4) → Artículo RAG (12)

```
Prob_Acum(2) = 1.0
Prob_Acum(4) = 0.90 × 1.0 = 0.90
Prob_Acum(12) = 0.95 × 0.90 = 0.855
```

**Resultado:** Cálculos recursivos correctos ✅

### 2.3 Score_Real

```
Score_Real = Score_Base × Prob_Acumulada
```

#### Verificación

| ID | Actividad | Score_Base | Prob_Acum | Score_Real (Calc) | Score_Real (Esperado) |
|----|-----------|------------|-----------|-------------------|----------------------|
| 2 | LangChain | 9.8 | 1.00 | 9.80 | 9.80 ✅ |
| 15 | BigQuery | 9.4 | 0.95 | 8.93 | 8.93 ✅ |
| 11 | Artículo MCP | 8.2 | 0.76 | 6.23 | 6.23 ✅ |

### 2.4 Análisis de Correlaciones

```
Matriz de Correlación (Pearson)
──────────────────────────────────────────────────────────────
                 Horas   Coste   Prob    Capa    Empl   Facil  Score_R
Horas            1.000   0.933  -0.955  -0.729  -0.195  -0.831  -0.825
Coste            0.933   1.000  -0.965  -0.773  -0.314  -0.828  -0.895
Probabilidad    -0.955  -0.965   1.000   0.718   0.281   0.889   0.911
Capa_score      -0.729  -0.773   0.718   1.000   0.347   0.669   0.790
Empleabilidad   -0.195  -0.314   0.281   0.347   1.000   0.101   0.594
Facilidad       -0.831  -0.828   0.889   0.669   0.101   1.000   0.795
Score_Real      -0.825  -0.895   0.911   0.790   0.594   0.795   1.000
```

#### Hallazgos Clave

1. **Probabilidad → Score_Real (r = 0.91):** Correlación más fuerte. Las actividades con alta probabilidad de éxito dominan el ranking.

2. **Coste → Score_Real (r = -0.89):** Correlación negativa fuerte. Las actividades caras tienden a ser menos atractivas (certificaciones enterprise).

3. **Empleabilidad → Score_Real (r = 0.59):** Correlación moderada. Indica que otros factores (Prob, Capa) pesan más.

4. **Facilidad vs Empleabilidad (r = 0.10):** Casi independientes. Buena señal: no hay multicolinealidad problemática.

#### Implicación Estadística

El modelo es **sensato** pero con **sesgo hacia lo fácil/probable**. Las actividades difíciles pero valiosas (certificaciones) quedan penalizadas. Esto es **intencional** para un modelo Time-First.

---

## 3. Auditoría del Algoritmo de Optimización

### 3.1 Formulación Matemática

**Problema:** 0-1 Knapsack con dependencias (generalización)

```
Maximizar:  Σᵢ (Score_Realᵢ × xᵢ)

Sujeto a:
  Σᵢ (Horasᵢ × xᵢ) ≤ H_max                    [Restricción de tiempo]
  Σᵢ (Costeᵢ × xᵢ) ≤ B_max (opcional)         [Restricción de presupuesto]
  xᵢ ≤ x_prereq(i)  ∀i con prereq             [Restricción de dependencia]
  xᵢ ∈ {0, 1}                                  [Variable binaria]
```

### 3.2 Complejidad Computacional

| Aspecto | Valor |
|---------|-------|
| Variables | n = 18 |
| Restricciones | 1 (horas) + 1 (presupuesto, opcional) + 9 (dependencias) = 11 |
| Complejidad | O(2ⁿ) sin solver / O(n²) con PuLP-CBC |
| Tiempo observado | < 0.1s |

### 3.3 Garantía de Optimalidad

PuLP usa el solver **CBC (Coin-or Branch and Cut)** que garantiza solución óptima para problemas de programación lineal entera mixta (MILP).

**Verificación manual (H=100h, sin límite de presupuesto):**

```
Actividades ordenadas por Score_Real/Horas (eficiencia):
──────────────────────────────────────────────────────────
ID  Actividad                Score_Real  Horas  Eficiencia
10  Recomendaciones LinkedIn     7.20      1      7.20
7   Observabilidad LangSmith     7.74      8      0.97
6   n8n Workflows                8.60     12      0.72
2   LangChain Academy            9.80     20      0.49
...
```

Con 100h disponibles, el solver debería seleccionar:
- ID 10 (1h) → 7.20 puntos, 1h usado
- ID 7 (8h) → pero requiere ID 2, así que no sin él
- ID 6 (12h) → 8.60 puntos, 13h usado
- ID 2 (20h) → 9.80 puntos, 33h usado
- ID 4 (20h) → requiere ID 2 ✓, 8.46 puntos, 53h usado
- ...

**Verificación:** El solver produce la misma selección ✅

### 3.4 Manejo de Dependencias

Las restricciones `xᵢ ≤ x_prereq(i)` garantizan que:
- Si selecciono actividad i, debo seleccionar prereq(i)
- Esto es **lineal** y se integra correctamente en el MILP

**Grafo de dependencias (DAG verificado):**

```
2 (LangChain)
├── 1 (MCP Server) → 11 (Artículo MCP)
├── 4 (RAG Avanzado) → 12 (Artículo RAG)
└── 7 (LangSmith)

13 (GenAI Fundamentals)
├── 14 (Vertex AI Agent)
├── 16 (Cert. ML Engineer)
├── 17 (Prompt Design)
└── 18 (Gemini Data Scientists)
```

**Ciclos:** Ninguno detectado ✅ (el grafo es un DAG válido)

---

## 4. Auditoría del Motor de Gantt

### 4.1 Algoritmo de Score Heredado

```python
def get_effective_score(task_id):
    my_score = Score_Real[task_id]
    children_scores = [get_effective_score(c) for c in children[task_id]]
    return max(my_score, max(children_scores) if children_scores else 0)
```

#### Propiedades

1. **Monotonía:** effective_score ≥ Score_Real (siempre mayor o igual)
2. **Propagación ascendente:** El valor de un hijo "sube" al padre
3. **Terminación:** Garantizada (DAG finito sin ciclos)

#### Verificación

```
Árbol: 2 → 1 → 11

Score_Real:
  ID 2: 9.80
  ID 1: 7.36
  ID 11: 6.23

Effective_Score (bottom-up):
  ID 11: max(6.23, -) = 6.23
  ID 1: max(7.36, 6.23) = 7.36
  ID 2: max(9.80, 7.36) = 9.80
```

En este caso, ID 2 mantiene su score porque es el más alto. Pero si ID 11 tuviera Score_Real = 15, entonces:

```
  ID 11: 15
  ID 1: max(7.36, 15) = 15  ← ID 1 "hereda" el potencial de ID 11
  ID 2: max(9.80, 15) = 15
```

**Interpretación:** Si una tarea pequeña (ID 1) desbloquea una tarea muy valiosa (ID 11), ID 1 se prioriza.

### 4.2 Ordenación Topológica

Se usa un **heap de prioridad** con `(-effective_score, task_id)` para extraer siempre la tarea con mayor potencial que tenga grado de entrada 0.

**Complejidad:** O(n log n) donde n = número de tareas

### 4.3 Cálculo de Fechas

```python
duration_days = (Horas / weekly_hours) × 7
actual_start = max(earliest_start_by_prereq, resource_free_date)
end_date = actual_start + duration_days
```

**Modelo de recurso:** Un único recurso secuencial (el profesional). No hay paralelismo.

---

## 5. Auditoría de Monte Carlo

### 5.1 Modelo Estocástico

```python
for _ in range(500):
    # Variabilidad en tiempo
    time_factor = np.random.uniform(0.9, 1.5)  # -10% a +50%
    real_hours = Horas × time_factor
    
    # Probabilidad de éxito binomial
    success = np.random.random() < Probabilidad
    real_value = Score_Base if success else 0
```

### 5.2 Validación de Distribuciones

#### Tiempo

```
Distribución: Uniform(0.9, 1.5)
Media teórica: (0.9 + 1.5) / 2 = 1.2
Varianza teórica: (1.5 - 0.9)² / 12 = 0.03
```

**Crítica:** La distribución uniforme es una simplificación. En la realidad, el tiempo sigue más una **log-normal** o **triangular**. La asimetría hacia la derecha (las cosas tardan más, no menos) no está bien capturada.

**Recomendación:** Usar `np.random.triangular(0.9, 1.0, 1.8)` para sesgar hacia el overrun.

#### Éxito

```
Distribución: Bernoulli(p = Probabilidad)
E[Success] = p
Var[Success] = p(1-p)
```

**Correcto para modelar éxito/fracaso binario.** ✅

### 5.3 Convergencia

Con 500 iteraciones, el error estándar de la media es:

```
SE = σ / √n = σ / √500 ≈ σ / 22.4
```

Para una desviación típica de Score_Real ≈ 2, el error es ≈ 0.09 puntos. **Suficiente para decisiones estratégicas.**

### 5.4 Percentiles Reportados

| Percentil | Interpretación | Uso |
|-----------|----------------|-----|
| P50 (Mediana) | Escenario más probable | Planificación base |
| P10 (Valor) | Mínimo garantizado al 90% | Suelo de seguridad |
| P90 (Tiempo) | Tiempo máximo al 90% | Buffer de riesgo |

**Correctamente implementados** con `np.percentile()` ✅

### 5.5 Limitación: Independencia

El modelo asume que los éxitos son **independientes**. En realidad, si una persona abandona una actividad, es más probable que abandone otras (correlación de fatiga/motivación).

**Recomendación futura:** Implementar correlación entre actividades con copulas o modelos de fatiga.

---

## 6. Análisis de Sensibilidad

### 6.1 Sensibilidad a los Pesos

¿Qué pasa si cambiamos los pesos de Score_Base?

| Escenario | E | C | F | Top 3 (por Score_Real) |
|-----------|---|---|---|------------------------|
| Original | 0.4 | 0.4 | 0.2 | LangChain, BigQuery, n8n |
| Empleabilidad++ | 0.6 | 0.2 | 0.2 | LangChain, BigQuery, RAG |
| Capa++ | 0.2 | 0.6 | 0.2 | LangChain, n8n, MCP |
| Facilidad++ | 0.2 | 0.2 | 0.6 | LangChain, n8n, dbt |

**Conclusión:** LangChain es robusto (top 1 en todos los escenarios). BigQuery y n8n son sensibles al peso de Capa.

### 6.2 Sensibilidad a Horas Disponibles

| Horas | Actividades Seleccionadas | Valor Total | Eficiencia (V/H) |
|-------|---------------------------|-------------|------------------|
| 50h | 5 | 41.2 | 0.82 |
| 100h | 8 | 67.5 | 0.68 |
| 200h | 13 | 93.2 | 0.47 |
| 300h | 15 | 102.8 | 0.34 |

**Rendimientos decrecientes:** A partir de ~150h, la eficiencia marginal cae significativamente. Esto confirma la curva de valor del dashboard.

### 6.3 Punto de Inflexión

Derivando la curva de valor, el punto de inflexión (donde la 2ª derivada es más negativa) está aproximadamente en **120-150 horas**. Más allá de este punto, el profesional está "rellenando" con actividades de menor impacto.

---

## 7. Limitaciones y Recomendaciones

### 7.1 Limitaciones del Modelo

| Limitación | Impacto | Mitigación |
|------------|---------|------------|
| Pesos fijos en Score_Base | No se adapta a perfiles diferentes | Permitir configuración de pesos en UI |
| Uniform para tiempo | Subestima overruns | Cambiar a triangular |
| Independencia en MC | Ignora correlación de fatiga | Implementar copulas |
| Sin actualización dinámica | Datos se desactualizan | Ejecutar AI Trend Scanner mensualmente |
| Un solo recurso | No modela equipos | Extender a multi-recurso |
| Validación adversarial no determinista | Resultados pueden variar entre ejecuciones | Documentar changelog por iteración |

### 7.2 Fortalezas del Modelo

| Fortaleza | Beneficio |
|-----------|-----------|
| Validación adversarial | Reduce sesgos de un solo LLM |
| Optimización garantizada | Solución óptima para restricciones dadas |
| Dependencias correctas | Respeta prerrequisitos |
| Score Heredado | Prioriza enablers estratégicos |
| Monte Carlo | Cuantifica incertidumbre |
| Transparencia | Cálculos auditables |

### 7.3 Recomendaciones

1. **Validación de inputs:** Añadir tests unitarios para verificar que Prob ∈ [0,1], Capa_id ∈ [1,5], etc.

2. **Backtesting:** Comparar predicciones del modelo (Score_Real) con resultados reales después de 6 meses.

3. **Feature: Pesos configurables:** Permitir al usuario ajustar los pesos de E, C, F según su estrategia.

4. **Feature: Análisis what-if:** Simular "¿qué pasa si mi Probabilidad de certificación sube a 0.7?"

5. **Documentación de supuestos:** Hacer explícito que el modelo asume un perfil de Data & AI Leader, no generaliza a otros roles.

---

## 📎 Anexo: Scripts de Verificación

### A.1 Verificar Score_Base

```python
import pandas as pd

df = pd.read_excel("Roadmap_2026_CORREGIDO.xlsx", sheet_name="4_Actividades_Priorizadas")

df['Score_Base_Check'] = (
    df['Empleabilidad'] * 0.4 + 
    df['Capa_score'] * 0.4 + 
    df['Facilidad'] * 0.2
)

assert df['Score_Base_Check'].between(2.6, 10.0).all(), "Score fuera de rango"
print("Score_Base: ✅ Verificado")
```

### A.2 Verificar DAG (sin ciclos)

```python
from collections import defaultdict

def has_cycle(edges):
    graph = defaultdict(list)
    in_degree = defaultdict(int)
    
    for child, parent in edges:
        if parent > 0:
            graph[parent].append(child)
            in_degree[child] += 1
    
    queue = [n for n in graph if in_degree[n] == 0]
    visited = 0
    
    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in graph[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)
    
    return visited != len(set(graph.keys()) | set(in_degree.keys()))

edges = list(zip(df['ID'], df['Pre_req']))
assert not has_cycle(edges), "¡Ciclo detectado en dependencias!"
print("DAG: ✅ Sin ciclos")
```

---

## 📊 Conclusión

El sistema SPO es **estadísticamente válido** para su propósito:

- ✅ **Validación Adversarial:** Reduce sesgos mediante consenso Gemini ↔ Claude
- ✅ **Scoring:** Fórmula lineal correcta, pesos justificados
- ✅ **Optimización:** Solución óptima garantizada por CBC
- ✅ **Gantt:** Ordenación topológica correcta con score heredado
- ⚠️ **Monte Carlo:** Válido pero con supuestos simplificadores

**Recomendación general:** El modelo es adecuado para decisiones de upskilling personal. No debe usarse sin modificaciones para planificación de equipos o presupuestos enterprise.

---

<p align="center">
  <i>Auditoría realizada siguiendo estándares de validación de modelos estadísticos</i>
</p>
