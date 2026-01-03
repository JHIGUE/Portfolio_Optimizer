# AI Trend Scanner v2.1

Prompt de investigación para generar el dataset de actividades de upskilling.
Ejecutar en Claude con acceso a web search.

---

## CONTEXTO

Actúa como AI Research Analyst especializado en tendencias de upskilling para perfiles de Data & AI Leadership.

Mi perfil: Data & AI Leader | Head of Data | Architect & Strategist | Multi-Cloud (Azure/GCP/AWS) | Analytics & Governance

Mis fortalezas: SQL avanzado, Python, Power BI, arquitectura de datos, ETL/ELT, gobernanza de datos, gestión de stakeholders senior.

Fecha de ejecución: [HOY]

---

## ROADMAP ACTUAL (para comparativa)

Formula de verificacion: `Score_Real = ((Empleabilidad × 0.4) + (Capa_score × 0.4) + (Facilidad × 0.2)) × Prob_Acumulada`

| ID | Actividad | Score_Real | Capa_score | Empleabilidad | Facilidad | Prob |
|----|-----------|------------|------------|---------------|-----------|------|
| (completar con roadmap actual) |

---

## FASE 1: BUSQUEDA DE FUENTES

Ejecuta web search para cada query:

- Gartner top strategic technology trends 2026 AI agents
- LangChain state of AI agents report 2026
- McKinsey state of AI enterprise adoption 2025 2026
- Google Cloud Vertex AI Agent Builder 2026
- RAG retrieval augmented generation market trends 2026
- AI governance observability LangSmith tools 2026
- LinkedIn AI data architect jobs skills demand 2026
- Forrester AI predictions 2026 enterprise

---

## FASE 2: IDENTIFICACION DE ACTIVIDADES

De cada fuente, extrae:
- Herramientas/frameworks emergentes
- Skills demandados en job postings
- Certificaciones o cursos relevantes
- Proyectos practicos con alto ROI

---

## FASE 3: DETECCION DE SESGOS (OBLIGATORIO)

Para CADA actividad identificada, evalua estos 3 sesgos:

### HYPE_BIAS (Sobrevaloracion de lo nuevo)

Senales de alerta:
- Solo aparece en blogs de marketing, no en reports tecnicos
- Usa superlativos excesivos ("revolucionario", "game-changer")
- No hay casos de uso en produccion documentados
- Metricas vagas sin datos concretos

Flag: HYPE_BIAS = true/false
Si true: Reducir Empleabilidad en -2 puntos

### VENDOR_BIAS (Promocion de productos propios)

Senales de alerta:
- Solo aparece en documentacion oficial del vendor
- No hay validacion de analistas independientes
- Sin adopcion fuera del ecosistema del vendor

Flag: VENDOR_BIAS = true/false
Si true: Buscar validacion independiente. Si no existe, reducir Empleabilidad en -1

### SURVIVORSHIP_BIAS (Solo vemos lo que sobrevive)

Senales de alerta:
- Version 1.x sin track record
- Empresa/proyecto <2 anos de antiguedad
- Sin funding significativo o respaldo enterprise

Flag: SURVIVORSHIP_BIAS = true/false
Si true: Verificar GitHub stars, ultima actualizacion. Si <1K stars o sin updates en 6 meses, DESCARTAR.

---

## FASE 4: RED FLAGS - DESCARTE AUTOMATICO

DESCARTAR cualquier actividad que cumpla AL MENOS UNO:

| Red Flag | Criterio |
|----------|----------|
| Sin comunidad | GitHub stars <1K O sin commits en 6 meses |
| Fuente unica | Solo aparece en 1 de las 8 fuentes |
| Vendor menor | Certificacion de empresa sin presencia en Magic Quadrant |
| Sin aplicacion | No tiene conexion clara con SQL/Python/Data/Architecture |
| Obsolescencia | Tecnologia siendo reemplazada activamente |
| Costo prohibitivo | >500 EUR sin ROI demostrable |

---

## FASE 5: CLASIFICACION (Taxonomia)

| Capa_id | Capa_desc | Capa_score | Incluye |
|---------|-----------|------------|---------|
| 1 | Orchestration | 10 | Agentes, LangGraph, MCP, multi-agent, workflows |
| 2 | Governance | 9 | Observabilidad, evals, safety, LangSmith, AI TRiSM |
| 3 | Data & Memory | 9 | RAG, vector DBs, embeddings, BigQuery Vector |
| 4 | Models (LLMs) | 7 | Prompting, fine-tuning, Gemini, Claude, GPT |
| 5 | Infrastructure | 5 | Cloud certs, MLOps, deployment, compute |

Tipos validos: Formacion IA | IA Practica | Certificacion | Visibilidad | Networking

---

## FASE 6: EVALUACION CON JUSTIFICACION

Para cada actividad NO descartada:

### Empleabilidad (1-10)

| Valor | Criterio | Evidencia requerida |
|-------|----------|---------------------|
| 10 | >50% job postings, Gartner top 3 | URL busqueda + cita Gartner |
| 9 | >30% job postings, "emergente" | URL busqueda + cita report |
| 8 | Multiples fuentes (3+) | Lista de 3+ fuentes |
| 7 | Util, no diferenciador | 1-2 menciones |
| 6 | Commoditizado | Evidencia saturacion |

### Facilidad (1-10) - Para perfil SQL/Python/Data Architecture

| Valor | Criterio | Justificacion requerida |
|-------|----------|-------------------------|
| 10 | Extension directa SQL/Python | Que skill aplica directamente |
| 9 | Curva <1 semana | Por que es rapido |
| 8 | Conceptos familiares | Que conceptos transfieren |
| 7 | Transferencia parcial | Que es nuevo vs conocido |
| 6 | Curva >40h | Que hay que aprender desde cero |
| 5 | Dominio nuevo | Por que no hay base |

### Probabilidad (0.0-1.0)

| Valor | Criterio |
|-------|----------|
| 1.0 | Gratuito, sin examen |
| 0.95 | Proyecto practico claro |
| 0.9 | Requiere dedicacion |
| 0.8 | Proyecto complejo |
| 0.5 | Certificacion con examen |
| 0.4 | Muy dificil/ambicioso |

---

## FASE 7: CALCULO DE SCORES (AUDITABLE)

```
Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)

Prob_Acumulada:
- Si Pre_req = 0: Prob_Acum = Probabilidad
- Si Pre_req > 0: Prob_Acum = Probabilidad * Prob_Acum(actividad Pre_req)

Score_Real = Score_Base * Prob_Acum
```

MOSTRAR EL CALCULO COMPLETO para cada actividad nueva.

---

## FASE 8: OUTPUT ESTRUCTURADO

Genera el output en este orden exacto (9 secciones):

### 1. RESUMEN EJECUTIVO
- Tendencia #1 identificada
- Tendencia #2 identificada
- Skill con mayor demanda
- Skill en declive (alerta)
- Recomendacion principal

### 2. ANALISIS DE SESGOS DETECTADOS
Tabla: Actividad | HYPE_BIAS | VENDOR_BIAS | SURVIVORSHIP_BIAS | Ajuste | Razon

### 3. ACTIVIDADES DESCARTADAS
Tabla: Actividad | Red Flag | Motivo | Verificacion

### 4. TABLA TOP 20
Ordenada por Score_Real DESC:
Rank | ID | Actividad | Tipo | Horas | Coste | Pre_req | Prob | Capa_id | Capa_score | Empl | Facil | Score_Base | Prob_Acum | Score_Real

### 5. JUSTIFICACIONES TOP 10
Para cada actividad:
- Empleabilidad [X]: Cita + URL
- Facilidad [X]: Razonamiento para perfil SQL/Python
- Capa [X]: Por que esta capa
- Sesgos detectados
- Riesgo principal

### 6. ALERTAS DE OBSOLESCENCIA
Actividades del roadmap actual que deberian salir:
ID | Actividad | Score Actual | Motivo | Reemplazar Por

### 7. COMPARATIVA VS ROADMAP ANTERIOR

#### Actividades Nuevas
Para cada una, justificar clasificacion y calculo

#### Actividades que Salen
ID | Actividad | Score | Motivo | Fuente

#### Actividades que Suben (delta >= 0.5)
ID | Actividad | Antes | Ahora | Componente que cambio | Por que

#### Actividades que Bajan (delta >= 0.5)
ID | Actividad | Antes | Ahora | Componente que cambio | Por que

### 8. METADATA DE EJECUCION

```yaml
fecha_ejecucion: YYYY-MM-DD
fuentes_consultadas:
  - nombre: "..."
    url: "..."
    fecha_publicacion: "..."
    datos_extraidos: "..."

estadisticas:
  actividades_identificadas_total: X
  actividades_descartadas_red_flags: X
  actividades_con_hype_bias: X
  actividades_con_vendor_bias: X
  actividades_nuevas_para_roadmap: X
```

### 9. VALIDACION PRE-ENTREGA

Checklist:
- [ ] Todas las actividades nuevas tienen 5 componentes justificados
- [ ] Todos los calculos son auditables
- [ ] Las fuentes tienen URLs reales
- [ ] Los Pre_req forman cadenas logicas (no circulares)
- [ ] TOP 20 ordenado por Score_Real
- [ ] Sesgos evaluados con razon documentada
- [ ] Comparativa completa

---

## RESTRICCIONES FINALES

NO incluir:
- Actividades con Empleabilidad < 6 (despues de ajustes)
- Actividades con Score_Real < 5.0
- Actividades con Red Flag activo
- Valores sin justificacion

PRIORIZAR:
- Capa 1, 2, 3 sobre 4, 5
- Verificar GitHub stars para herramientas open source
- Cruzar fuentes: minimo 2 menciones independientes
- Mostrar calculo completo para cada Score_Real nuevo
