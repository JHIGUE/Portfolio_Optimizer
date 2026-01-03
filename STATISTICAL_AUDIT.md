# AUDITORÍA ESTADÍSTICA: Strategic Portfolio Optimizer (SPO)

**Evaluador:** Estadístico Tester Senior  
**Fecha:** 2026-01-03  
**Versión evaluada:** SPO v2.1  
**Dataset:** Roadmap_2026_CORREGIDO.xlsx (N=18 actividades)

---

## RESUMEN EJECUTIVO

| Área | Puntuación | Comentario |
|------|------------|------------|
| Formulación matemática | 8/10 | Sólida, bien implementada |
| Implementación algoritmos | 9/10 | Correcta y eficiente |
| Validez estadística | 7/10 | Supuestos razonables |
| Robustez metodológica | 8/10 | Ranking estable ante cambios de pesos |
| Interpretabilidad | 8/10 | Clara para usuario final |

**Veredicto global: 8.0/10** - Sistema robusto con fundamentos matemáticos correctos. Adecuado para uso profesional con las limitaciones documentadas.

---

## 1. VALIDACIÓN DE LA FÓRMULA DE SCORING

### 1.1 Especificación

```
Score_Base = (Empleabilidad × 0.4) + (Capa_score × 0.4) + (Facilidad × 0.2)
Score_Real = Score_Base × Probabilidad_Acumulada
```

### 1.2 Verificación empírica

| Actividad | Empleab. | Capa | Facil. | Score_Base (calculado) |
|-----------|----------|------|--------|------------------------|
| LangChain Academy | 10 | 10 | 9 | (10×0.4)+(10×0.4)+(9×0.2) = **9.80** |
| MCP Server Prototype | 9 | 10 | 8 | (9×0.4)+(10×0.4)+(8×0.2) = **9.20** |
| Azure DP-203 | 6 | 5 | 6 | (6×0.4)+(5×0.4)+(6×0.2) = **5.60** |

**Verificación:** Los cálculos en el código coinciden exactamente con la fórmula documentada.

### 1.3 Distribución de inputs

| Variable | Rango | Media | Mediana | CV |
|----------|-------|-------|---------|-----|
| Empleabilidad | [4, 10] | 7.78 | 8.0 | 21.9% |
| Facilidad | [5, 10] | 8.11 | 9.0 | 18.9% |
| Capa_score | [5, 10] | 8.28 | 9.0 | 21.8% |
| Score_Base | [5.40, 9.80] | 8.04 | 8.40 | 16.5% |

**Observación:** Buena varianza en los inputs. No hay clustering excesivo en valores extremos.

### 1.4 Crítica de pesos

| Aspecto | Evaluación |
|---------|------------|
| Justificación declarada | Razonable: Empleabilidad y Capa como drivers principales, Facilidad como tiebreaker |
| Escalas de inputs | Capa_score [5-10] vs otros [1-10]. Implica que Capa tiene menor rango de contribución real |
| Análisis de sensibilidad | Ranking estable (Spearman >0.93) ante cambios de ±10% en pesos |

**Recomendación:** Documentar que los pesos son criterio experto, no derivados empíricamente. La estabilidad del ranking sugiere que son razonables.

---

## 2. ANÁLISIS DE PROBABILIDAD ACUMULADA

### 2.1 Implementación

```
Prob_Acum(tarea) = Prob_propia × Prob_Acum(padre)
```

Recursiva con memoización. Correcta.

### 2.2 Impacto en el dataset

| Métrica | Valor |
|---------|-------|
| Score_Base total | 144.80 pts |
| Score_Real total | 126.42 pts |
| **Pérdida por incertidumbre** | **18.38 pts (12.7%)** |
| Tareas con Prob_Acum < 0.8 | 4 de 18 |

### 2.3 Cadenas de mayor profundidad

| Cadena | Prob_Acum |
|--------|-----------|
| 2 → 1 → 11 (Artículo #1 MCP) | 0.760 |
| 2 → 4 → 12 (Artículo #2 RAG) | 0.855 |
| 13 → 16 (Cert. Google ML) | 0.500 |

**Observación:** Las cadenas de dependencia penalizan correctamente las tareas con prerrequisitos inciertos.

---

## 3. ANÁLISIS DE CORRELACIONES

### 3.1 Matriz de correlación (variables clave)

|  | Empleab. | Facil. | Capa | Horas | Coste | Prob |
|--|----------|--------|------|-------|-------|------|
| Empleabilidad | 1.00 | 0.10 | 0.35 | -0.20 | -0.31 | 0.28 |
| Facilidad | 0.10 | 1.00 | 0.67 | -0.83 | -0.83 | 0.89 |
| Capa_score | 0.35 | 0.67 | 1.00 | -0.73 | -0.77 | 0.72 |
| Horas | -0.20 | -0.83 | -0.73 | 1.00 | **0.93** | -0.96 |
| Coste | -0.31 | -0.83 | -0.77 | **0.93** | 1.00 | -0.97 |
| Probabilidad | 0.28 | 0.89 | 0.72 | -0.96 | -0.97 | 1.00 |

### 3.2 Hallazgos críticos

| Correlación | Valor | Interpretación |
|-------------|-------|----------------|
| **Horas-Coste** | 0.93 | ALTA. Las restricciones son casi redundantes. |
| **Horas-Probabilidad** | -0.96 | Tareas largas = menos probable completar |
| **Empleabilidad-Facilidad** | 0.10 | Independientes. Bien: no hay colinealidad en inputs. |
| **Score_Base-Probabilidad** | 0.74 | Tareas valiosas tienden a ser más factibles |

**Implicación para Knapsack:** La alta correlación Horas-Coste significa que una de las restricciones es casi redundante. En la práctica, HORAS es siempre la restricción binding.

---

## 4. ANÁLISIS DEL ALGORITMO KNAPSACK

### 4.1 Especificación

```
Maximizar: Σ Score_Real[i] × x[i]
Sujeto a:
  Σ Coste[i] × x[i] ≤ Presupuesto
  Σ Horas[i] × x[i] ≤ Horas_disponibles
  x[hijo] ≤ x[padre]  ∀ dependencias
  x[i] ∈ {0, 1}
```

### 4.2 Soluciones por escenario

| Escenario | Items | Score_Real | Coste (%) | Horas (%) | Binding |
|-----------|-------|------------|-----------|-----------|---------|
| Restrictivo (€100, 100h) | 9/18 | 72.43 | 70% | 94% | HORAS |
| Moderado (€300, 200h) | 14/18 | 112.33 | 40% | 100% | HORAS |
| **Default (€650, 300h)** | **16/18** | **121.46** | **49%** | **87%** | **HORAS** |
| Holgado (€1000, 500h) | 18/18 | 126.42 | 68% | 88% | HORAS |

### 4.3 Hallazgo crítico

**La restricción de presupuesto NUNCA es binding.** En el escenario default:
- Se usan €320 de €650 disponibles (49%)
- Se usan 262h de 300h disponibles (87%)

**Implicación:** El slider de presupuesto en la UI tiene poco impacto práctico. El recurso realmente escaso son las HORAS.

### 4.4 Actividades excluidas (escenario default)

| ID | Actividad | Score_Real | Coste | Horas | Razón exclusión |
|----|-----------|------------|-------|-------|-----------------|
| 8 | Azure DP-203 | 2.80 | 165€ | 80h | Bajo Score_Real, alto coste/tiempo |
| 9 | GCP Professional | 2.16 | 200€ | 100h | Peor Score_Real del dataset |

**Observación:** El algoritmo correctamente descarta las certificaciones cloud genéricas por su bajo ROI.

---

## 5. ANÁLISIS MONTE CARLO

### 5.1 Resultados de simulación (N=1000)

| Métrica | Horas | Valor |
|---------|-------|-------|
| Media | 530.9h | 129.3 pts |
| Std | 27.4h | 8.5 pts |
| IC 95% | [474.5, 581.8] | [111.2, 144.8] |
| P50 (mediana) | 531.7h | - |
| P90 (pesimista) | 565.6h | - |
| P10 (pesimista) | - | 117.8 pts |

### 5.2 Test de normalidad

| Variable | p-value | Resultado |
|----------|---------|-----------|
| Horas | 0.036 | No Normal |
| Valor | <0.001 | No Normal |

**Explicación:** Las distribuciones no son normales porque:
- Factor tiempo U(0.9, 1.5) genera distribución uniforme
- Éxito por Bernoulli con N=18 no converge a normal (N muy pequeño)

**Impacto práctico:** Los percentiles (P10, P50, P90) siguen siendo válidos no-paramétricamente. Los histogramas en la UI son informativos.

### 5.3 Crítica del modelo Monte Carlo

| Aspecto | Implementación actual | Mejora potencial |
|---------|----------------------|------------------|
| Factor tiempo | U(0.9, 1.5) | Distribución PERT con (min, moda, max) |
| Independencia | Tareas independientes | Correlación: si padre falla, hijo falla |
| Distribución éxito | Bernoulli | Beta si hay éxito parcial |

---

## 6. ANÁLISIS DE SENSIBILIDAD DE PESOS

### 6.1 Escenarios probados

| Escenario | Empleab. | Capa | Facil. |
|-----------|----------|------|--------|
| Original | 0.40 | 0.40 | 0.20 |
| Más Empleabilidad | 0.50 | 0.30 | 0.20 |
| Más Capa | 0.30 | 0.50 | 0.20 |
| Más Facilidad | 0.30 | 0.30 | 0.40 |
| Equiponderado | 0.33 | 0.33 | 0.34 |

### 6.2 Estabilidad del Top 5

**Actividad #1 en TODOS los escenarios:** LangChain Academy (ID 2)

**Top 5 consistente:** IDs 2, 15, 6, 4, 5 aparecen en todas las configuraciones.

### 6.3 Correlación de rankings (Spearman)

| Comparación | Correlación |
|-------------|-------------|
| Original vs Más Empleabilidad | 0.972 |
| Original vs Más Capa | 0.964 |
| Original vs Más Facilidad | 0.958 |
| Más Empleabilidad vs Más Capa | 0.936 |

**Conclusión:** El ranking es MUY ESTABLE ante cambios de pesos. Esto sugiere que:
1. Los pesos elegidos son razonables
2. Los datos tienen estructura clara (no hay ambigüedad)
3. Pequeños errores en los pesos no cambiarían las decisiones

---

## 7. ANÁLISIS POR CAPA (TAXONOMÍA)

### 7.1 Distribución de actividades

| Capa | N | Score_Base medio | Horas total | Coste total |
|------|---|------------------|-------------|-------------|
| Orchestration | 5 | 8.96 | 90h | €70 |
| Data & Memory | 5 | 8.84 | 70h | €50 |
| Governance | 2 | 7.90 | 9h | €0 |
| Models (LLMs) | 3 | 7.73 | 33h | €0 |
| Infrastructure | 3 | 5.60 | 240h | €565 |

### 7.2 Observaciones

1. **Orchestration** domina en Score_Base medio y tiene coste/hora razonable
2. **Infrastructure** tiene el peor Score_Base y concentra 82% del coste total
3. La taxonomía refleja correctamente el valor estratégico declarado

---

## 8. COMPARATIVA CON PRODUCTOS SIMILARES

### 8.1 Metodologías de priorización

| Producto | Metodología | SPO equivale | Ventaja SPO |
|----------|-------------|--------------|-------------|
| **Jira Portfolio** | WSJF (Weighted Shortest Job First) | Score_Real / Horas | Integra dependencias + probabilidad |
| **ProductBoard** | RICE (Reach, Impact, Confidence, Effort) | Empleabilidad ≈ Reach, Capa ≈ Impact, Facilidad ≈ 1/Effort | Taxonomía especializada en IA |
| **Asana Goals** | OKR alignment | N/A | Optimización matemática vs manual |

### 8.2 Solvers de optimización

| Solver | Uso recomendado | SPO usa |
|--------|-----------------|---------|
| PuLP/CBC | N < 1000, LP/MIP básico | Sí (correcto) |
| Gurobi | N > 1000, multi-objetivo | No (innecesario) |
| OR-Tools | Routing, scheduling | No (diferente problema) |

### 8.3 Simuladores de riesgo

| Característica | @RISK/Crystal Ball | SPO |
|----------------|-------------------|-----|
| Distribuciones | Normal, PERT, Beta, etc. | Uniforme, Bernoulli |
| Correlaciones | Matrices completas | Independencia |
| Tornado charts | Sí | No |
| Suficiente para N=18 | Overkill | Adecuado |

---

## 9. FORTALEZAS DEL SISTEMA

1. **Fórmula transparente y auditable** - Cada Score_Real es trazable
2. **Ranking estable** - Robusto ante cambios de pesos (Spearman >0.93)
3. **Taxonomía coherente** - Orchestration > Governance > Data > Models > Infrastructure se refleja en los datos
4. **Knapsack correcto** - Garantiza óptimo global, respeta dependencias
5. **Gantt con Score Heredado** - Concepto innovador de priorización
6. **Identificación correcta de perdedores** - Azure DP-203, GCP Professional quedan fuera

---

## 10. DEBILIDADES Y RECOMENDACIONES

### 10.1 Debilidades

| Debilidad | Severidad | Recomendación |
|-----------|-----------|---------------|
| Presupuesto nunca es binding | Baja | Documentar que HORAS es la restricción real |
| Monte Carlo sin correlaciones | Media | Implementar fallo en cascada para dependencias |
| Horas-Coste r=0.93 | Baja | Una restricción es casi redundante |
| "Pareto" mal nombrado | Baja | Renombrar a "Curva de Eficiencia" |
| N=18 pequeño para inferencia | Media | Aumentar dataset o documentar como limitación |

### 10.2 Sugerencia: Frontera de Posibilidades de Producción

El usuario pregunta si tiene sentido añadir una FPP con € y Horas.

**Respuesta:** Sí, tendría sentido un gráfico bidimensional que muestre:
- Eje X: Horas
- Eje Y: €
- Color/tamaño: Score_Real obtenido
- Isolíneas donde Score = 80, 100, 120...

Esto visualizaría mejor qué restricción es binding en cada zona.

---

## 11. VEREDICTO FINAL

### Puntuación detallada

| Criterio | Peso | Puntuación | Contribución |
|----------|------|------------|--------------|
| Correctitud matemática | 25% | 9/10 | 2.25 |
| Implementación algoritmos | 25% | 9/10 | 2.25 |
| Validez estadística | 20% | 7/10 | 1.40 |
| Usabilidad/UX | 15% | 8/10 | 1.20 |
| Documentación | 15% | 7/10 | 1.05 |
| **TOTAL** | 100% | | **8.15/10** |

### Para uso como portfolio

**APROBADO.** Demuestra:
- Pensamiento de arquitecto (LLM + algoritmo determinista)
- Implementación correcta de optimización combinatoria
- Análisis de riesgo con Monte Carlo
- Capacidad de documentar decisiones técnicas (ADRs)

### Para toma de decisiones reales

**APTO CON RESERVAS.** El sistema produce recomendaciones coherentes y el ranking es estable. Las limitaciones (N pequeño, Monte Carlo simplificado) están documentadas.

---

*Fin del informe de auditoría estadística.*
