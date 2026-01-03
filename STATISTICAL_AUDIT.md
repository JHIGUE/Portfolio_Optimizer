# Auditoria Estadistica: Strategic Portfolio Optimizer (SPO)

**Evaluador:** Estadístico Tester Senior  
**Fecha:** 2026-01-03  
**Versión evaluada:** SPO v2.2 (Time-First)  
**Dataset:** Roadmap_2026.xlsx (N=18 actividades)

---

## Resumen Ejecutivo

| Área | Puntuación | Comentario |
|------|------------|------------|
| Formulación matemática | 8/10 | Sólida, bien implementada |
| Implementación algoritmos | 9/10 | Correcta y eficiente |
| Validez estadística | 7/10 | Supuestos razonables |
| Robustez metodológica | 8/10 | Ranking estable ante cambios de pesos |
| Modelo Time-First | 9/10 | Justificado por evidencia empírica |

**Veredicto global: 8.2/10** - Sistema robusto con fundamentos matemáticos correctos y modelo conceptual honesto.

---

## 1. Justificación del Modelo Time-First

### 1.1 Evidencia empírica

| Escenario | Uso Horas | Uso Presupuesto | Restricción Binding |
|-----------|-----------|-----------------|---------------------|
| Restrictivo (100h, 100 EUR) | 94% | 70% | HORAS |
| Moderado (200h, 300 EUR) | 100% | 40% | HORAS |
| Default (300h, 650 EUR) | 87% | 49% | HORAS |
| Holgado (500h, 1000 EUR) | 88% | 68% | HORAS |

**Conclusión:** En el 100% de los escenarios, Horas es la restricción limitante.

### 1.2 Correlación Horas-Coste

```
r = 0.93 (casi perfecta)
```

Las dos restricciones son casi redundantes. Mantener ambas como inputs iguales confunde al usuario.

### 1.3 Distribución de costes

- 72% de actividades son gratuitas o cuestan menos de 50 EUR
- Solo 3 actividades cuestan más de 100 EUR
- Esas 3 tienen los peores Score_Real del dataset

---

## 2. Validación de la Fórmula de Scoring

### 2.1 Especificación

```
Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)
Score_Real = Score_Base * Probabilidad_Acumulada
```

### 2.2 Distribución de inputs

| Variable | Rango | Media | CV |
|----------|-------|-------|-----|
| Empleabilidad | [4, 10] | 7.78 | 21.9% |
| Facilidad | [5, 10] | 8.11 | 18.9% |
| Capa_score | [5, 10] | 8.28 | 21.8% |
| Score_Base | [5.40, 9.80] | 8.04 | 16.5% |

### 2.3 Ranking Top 5

| Rank | Actividad | Score_Real |
|------|-----------|------------|
| 1 | LangChain Academy | 9.80 |
| 2 | BigQuery ML Vector Search | 8.93 |
| 3 | n8n Workflows | 8.60 |
| 4 | RAG Avanzado | 8.46 |
| 5 | dbt Fundamentals | 8.36 |

---

## 3. Análisis de Sensibilidad de Pesos

### 3.1 Escenarios probados

| Escenario | Empleab. | Capa | Facil. |
|-----------|----------|------|--------|
| Original | 0.40 | 0.40 | 0.20 |
| Más Empleabilidad | 0.50 | 0.30 | 0.20 |
| Más Capa | 0.30 | 0.50 | 0.20 |
| Más Facilidad | 0.30 | 0.30 | 0.40 |

### 3.2 Estabilidad del ranking

| Comparación | Correlación Spearman |
|-------------|----------------------|
| Original vs Más Empleabilidad | 0.972 |
| Original vs Más Capa | 0.964 |
| Original vs Más Facilidad | 0.958 |
| Más Empleabilidad vs Más Capa | 0.936 |

**Conclusión:** El ranking es MUY ESTABLE (todas las correlaciones mayores a 0.93). Los pesos elegidos son robustos.

---

## 4. Análisis del Knapsack Time-First

### 4.1 Nueva especificación

```
Maximizar: Sum(Score_Real[i] * x[i])
Sujeto a:
  Sum(Horas[i] * x[i]) <= Horas_disponibles   # SIEMPRE ACTIVA
  Sum(Coste[i] * x[i]) <= Presupuesto         # SOLO SI budget != None
  x[hijo] <= x[padre]                          # Dependencias
  x[i] in {0, 1}
```

### 4.2 Actividades excluidas (escenario default)

| ID | Actividad | Score_Real | Horas | Razón |
|----|-----------|------------|-------|-------|
| 8 | Azure DP-203 | 2.80 | 80h | Bajo valor, alto tiempo |
| 9 | GCP Professional | 2.16 | 100h | Peor Score_Real del dataset |

**Observación:** El algoritmo correctamente prioriza actividades de alto valor por hora.

---

## 5. Probabilidad Acumulada

### 5.1 Impacto en el dataset

| Métrica | Valor |
|---------|-------|
| Score_Base total | 144.80 pts |
| Score_Real total | 126.42 pts |
| Pérdida por incertidumbre | 18.38 pts (12.7%) |

### 5.2 Cadenas de mayor profundidad

| Cadena | Prob_Acum |
|--------|-----------|
| 2 -> 1 -> 11 | 0.760 |
| 2 -> 4 -> 12 | 0.855 |
| 13 -> 16 | 0.500 |

---

## 6. Monte Carlo

### 6.1 Resultados (N=1000)

| Métrica | Horas | Valor |
|---------|-------|-------|
| Media | 530.9h | 129.3 pts |
| IC 95% | [474.5, 581.8] | [111.2, 144.8] |
| P90 pesimista | 565.6h | - |
| P10 pesimista | - | 117.8 pts |

### 6.2 Limitaciones

- Factor tiempo U(0.9, 1.5) es heurístico
- Asume independencia entre tareas
- N=18 pequeño para inferencia robusta

---

## 7. Comparativa con Productos Similares

| Producto | Metodología | SPO vs |
|----------|-------------|--------|
| Jira Portfolio | WSJF | SPO integra dependencias + probabilidad |
| ProductBoard | RICE | SPO tiene taxonomía especializada en IA |
| @RISK | Monte Carlo completo | SPO más simple, suficiente para N pequeño |

---

## 8. Fortalezas del Modelo Time-First

1. **Conceptualmente honesto:** Refleja que el tiempo es el verdadero cuello de botella
2. **UI más simple:** Un slider principal, uno opcional
3. **Coste como output:** El usuario ve el coste como consecuencia, no como decisión
4. **Justificado empíricamente:** 100% de escenarios confirman que Horas es binding

---

## 9. Debilidades y Recomendaciones

| Debilidad | Severidad | Recomendación |
|-----------|-----------|---------------|
| Pesos heurísticos | Media | Documentar como criterio experto |
| Monte Carlo sin correlaciones | Media | Implementar fallo en cascada |
| N=18 pequeño | Baja | Ampliar dataset |
| Sin back-testing | Media | Comparar con resultados reales |

---

## 10. Veredicto Final

### Puntuación detallada

| Criterio | Peso | Puntuación | Contribución |
|----------|------|------------|--------------|
| Correctitud matemática | 25% | 9/10 | 2.25 |
| Implementación algoritmos | 25% | 9/10 | 2.25 |
| Validez estadística | 20% | 7/10 | 1.40 |
| Modelo Time-First | 15% | 9/10 | 1.35 |
| Documentación | 15% | 7/10 | 1.05 |
| **TOTAL** | 100% | | **8.30/10** |

### Para uso como portfolio

**APROBADO.** Demuestra pensamiento de arquitecto, implementación correcta, y capacidad de iterar basándose en evidencia (cambio a Time-First).

### Para toma de decisiones reales

**APTO.** El modelo Time-First es más honesto y útil que la versión anterior con doble restricción.

---

*Fin del informe de auditoría estadística.*
