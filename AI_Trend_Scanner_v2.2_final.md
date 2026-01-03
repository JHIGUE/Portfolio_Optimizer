# AI Trend Scanner v2.2

Prompt de investigación para generar el dataset de actividades de upskilling.
Ejecutar en Claude con acceso a web search.

---

## CONTEXTO

Actúa como AI Research Analyst especializado en tendencias de upskilling para perfiles de Data & AI Leadership.

Mi perfil: Data & AI Leader | Head of Data | Architect & Strategist | Multi-Cloud (Azure/GCP/AWS) | Analytics & Governance

Mis fortalezas: SQL avanzado, Python, Power BI, arquitectura de datos, ETL/ELT, gobernanza de datos, gestión de stakeholders senior.

Fecha de ejecución: [HOY]

---

## REGLA CRÍTICA: VERIFICACIÓN DE DATOS

Para CADA columna del esquema, aplicar esta lógica:

| Columna | Fuente de datos | Acción si no hay dato verificable |
|---------|-----------------|-----------------------------------|
| Horas | URL oficial del curso/certificación | Buscar en web. Si no hay dato contrastado, marcar "VERIFICAR: ~Xh" |
| Coste | URL oficial (pricing page) | Buscar en web. Si no hay dato contrastado, marcar "VERIFICAR: ~X€" |
| Empleabilidad | Web search de job postings + reports | Estimar basado en evidencia encontrada |
| Facilidad | Análisis de skills transferibles | Estimar basado en tu perfil |
| Probabilidad | Criterio según tabla de probabilidades | Asignar según criterios definidos |
| Capa_id/Capa_score | Taxonomía fija | Usar tabla de taxonomía |
| URL_Fuente | Búsqueda web | Obligatorio: URL oficial o mejor fuente encontrada |

**Prioridad de fuentes para Horas y Coste:**
1. URL oficial del curso/certificación/herramienta
2. Plataformas de cursos (Coursera, Udemy, Cloud Skills Boost, etc.)
3. Reviews/blogs con datos específicos citados
4. Si ninguna fuente tiene datos → "VERIFICAR: ~estimación"

---

## ROADMAP ACTUAL (INPUT)

El usuario proporcionará el roadmap actual con este esquema:

```
ID | Actividad | Tipo | Horas | Coste | Pre_req | Probabilidad | Capa_id | Capa_desc | Capa_score | Empleabilidad | Facilidad | URL_Fuente
```

**IMPORTANTE:** Para actividades existentes, mantener Horas y Coste del input original a menos que la búsqueda web revele datos más precisos.

Formula de verificación: `Score_Real = ((Empleabilidad × 0.4) + (Capa_score × 0.4) + (Facilidad × 0.2)) × Prob_Acumulada`

---

## FASE 1: BÚSQUEDA DE FUENTES

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

## FASE 2: IDENTIFICACIÓN DE ACTIVIDADES

De cada fuente, extrae:
- Herramientas/frameworks emergentes
- Skills demandados en job postings
- Certificaciones o cursos relevantes
- Proyectos prácticos con alto ROI

**Para cada actividad nueva identificada:**
1. Buscar URL oficial
2. Extraer Horas y Coste de la fuente
3. Si no hay datos exactos, buscar en fuentes secundarias
4. Documentar la URL_Fuente usada

---

## FASE 3: DETECCIÓN DE SESGOS (OBLIGATORIO)

Para CADA actividad identificada, evalúa estos 3 sesgos:

### HYPE_BIAS (Sobrevaloración de lo nuevo)

Señales de alerta:
- Solo aparece en blogs de marketing, no en reports técnicos
- Usa superlativos excesivos ("revolucionario", "game-changer")
- No hay casos de uso en producción documentados
- Métricas vagas sin datos concretos

Flag: HYPE_BIAS = true/false
Si true: Reducir Empleabilidad en -2 puntos

### VENDOR_BIAS (Promoción de productos propios)

Señales de alerta:
- Solo aparece en documentación oficial del vendor
- No hay validación de analistas independientes
- Sin adopción fuera del ecosistema del vendor

Flag: VENDOR_BIAS = true/false
Si true: Buscar validación independiente. Si no existe, reducir Empleabilidad en -1

### SURVIVORSHIP_BIAS (Solo vemos lo que sobrevive)

Señales de alerta:
- Versión 1.x sin track record
- Empresa/proyecto <2 años de antigüedad
- Sin funding significativo o respaldo enterprise

Flag: SURVIVORSHIP_BIAS = true/false
Si true: Verificar GitHub stars, última actualización. Si <1K stars o sin updates en 6 meses, DESCARTAR.

---

## FASE 4: RED FLAGS - DESCARTE AUTOMÁTICO

DESCARTAR cualquier actividad que cumpla AL MENOS UNO:

| Red Flag | Criterio |
|----------|----------|
| Sin comunidad | GitHub stars <1K O sin commits en 6 meses |
| Fuente única | Solo aparece en 1 de las 8 fuentes |
| Vendor menor | Certificación de empresa sin presencia en Magic Quadrant |
| Sin aplicación | No tiene conexión clara con SQL/Python/Data/Architecture |
| Obsolescencia | Tecnología siendo reemplazada activamente |
| Costo prohibitivo | >500 EUR sin ROI demostrable |

---

## FASE 5: CLASIFICACIÓN (Taxonomía)

| Capa_id | Capa_desc | Capa_score | Incluye |
|---------|-----------|------------|---------|
| 1 | Orchestration | 10 | Agentes, LangGraph, MCP, multi-agent, workflows |
| 2 | Governance | 9 | Observabilidad, evals, safety, LangSmith, AI TRiSM |
| 3 | Data & Memory | 9 | RAG, vector DBs, embeddings, BigQuery Vector |
| 4 | Models (LLMs) | 7 | Prompting, fine-tuning, Gemini, Claude, GPT |
| 5 | Infrastructure | 5 | Cloud certs, MLOps, deployment, compute |

Tipos válidos: Formación IA | IA Práctica | Certificación | Visibilidad | Networking

---

## FASE 6: EVALUACIÓN CON JUSTIFICACIÓN

Para cada actividad NO descartada:

### Empleabilidad (1-10)

| Valor | Criterio | Evidencia requerida |
|-------|----------|---------------------|
| 10 | >50% job postings, Gartner top 3 | URL búsqueda + cita Gartner |
| 9 | >30% job postings, "emergente" | URL búsqueda + cita report |
| 8 | Múltiples fuentes (3+) | Lista de 3+ fuentes |
| 7 | Útil, no diferenciador | 1-2 menciones |
| 6 | Commoditizado | Evidencia saturación |

### Facilidad (1-10) - Para perfil SQL/Python/Data Architecture

| Valor | Criterio | Justificación requerida |
|-------|----------|-------------------------|
| 10 | Extensión directa SQL/Python | Qué skill aplica directamente |
| 9 | Curva <1 semana | Por qué es rápido |
| 8 | Conceptos familiares | Qué conceptos transfieren |
| 7 | Transferencia parcial | Qué es nuevo vs conocido |
| 6 | Curva >40h | Qué hay que aprender desde cero |
| 5 | Dominio nuevo | Por qué no hay base |

### Probabilidad (0.0-1.0)

| Valor | Criterio |
|-------|----------|
| 1.0 | Gratuito, sin examen |
| 0.95 | Proyecto práctico claro |
| 0.9 | Requiere dedicación |
| 0.8 | Proyecto complejo |
| 0.5 | Certificación con examen |
| 0.4 | Muy difícil/ambicioso |

---

## FASE 7: CÁLCULO DE SCORES (AUDITABLE)

```
Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)

Prob_Acumulada:
- Si Pre_req = 0: Prob_Acum = Probabilidad
- Si Pre_req > 0: Prob_Acum = Probabilidad * Prob_Acum(actividad Pre_req)

Score_Real = Score_Base * Prob_Acum
```

MOSTRAR EL CÁLCULO COMPLETO para cada actividad nueva.

---

## FASE 8: OUTPUT ESTRUCTURADO

Genera el output en este orden exacto (9 secciones):

### 1. RESUMEN EJECUTIVO
- Tendencia #1 identificada
- Tendencia #2 identificada
- Skill con mayor demanda
- Skill en declive (alerta)
- Recomendación principal

### 2. ANÁLISIS DE SESGOS DETECTADOS
Tabla: Actividad | HYPE_BIAS | VENDOR_BIAS | SURVIVORSHIP_BIAS | Ajuste | Razón

### 3. ACTIVIDADES DESCARTADAS
Tabla: Actividad | Red Flag | Motivo | Verificación

### 4. TABLA PRINCIPAL (ESQUEMA OBLIGATORIO)

**REGLA DE IDs:** Los IDs de actividades nuevas deben ser SECUENCIALES. Tomar el número más alto del roadmap actual y continuar desde ahí (ej: si el máximo es 18, la primera nueva es 19, luego 20, etc.). NO usar "NEW1", "NEW2" ni similares.

Ordenada por Score_Real DESC:

| ID | Actividad | Tipo | Horas | Coste | Pre_req | Probabilidad | Capa_id | Capa_desc | Capa_score | Empleabilidad | Facilidad | URL_Fuente |

**Columnas calculadas (mostrar aparte):**
| ID | Score_Base | Prob_Acum | Score_Real |

### 5. JUSTIFICACIONES TOP 10
Para cada actividad:
- Empleabilidad [X]: Cita + URL
- Facilidad [X]: Razonamiento para perfil SQL/Python
- Capa [X]: Por qué esta capa
- Horas/Coste: Fuente del dato (URL o "VERIFICAR")
- Sesgos detectados
- Riesgo principal

### 6. ALERTAS DE OBSOLESCENCIA
Actividades del roadmap actual que deberían salir:
ID | Actividad | Score Actual | Motivo | Reemplazar Por

### 7. COMPARATIVA VS ROADMAP ANTERIOR

#### Actividades Nuevas
Para cada una, justificar clasificación y cálculo

#### Actividades que Salen
ID | Actividad | Score | Motivo | Fuente

#### Actividades que Suben (delta >= 0.5)
ID | Actividad | Antes | Ahora | Componente que cambió | Por qué

#### Actividades que Bajan (delta >= 0.5)
ID | Actividad | Antes | Ahora | Componente que cambió | Por qué

### 8. DATOS PENDIENTES DE VERIFICAR

Lista de actividades donde Horas o Coste no pudieron confirmarse con fuente oficial:

| ID | Actividad | Campo | Valor estimado | URL consultada | Acción requerida |
|----|-----------|-------|----------------|----------------|------------------|

### 9. METADATA DE EJECUCIÓN

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
  datos_verificados: X
  datos_pendientes_verificar: X
  
max_id_usado: X  # Para referencia de próxima ejecución
```

### 10. VALIDACIÓN PRE-ENTREGA

Checklist:
- [ ] Todas las actividades tienen los 12 campos del esquema
- [ ] IDs nuevos son secuenciales (no "NEW*")
- [ ] Todas las actividades tienen URL_Fuente
- [ ] Horas y Coste vienen de búsqueda web o marcados "VERIFICAR"
- [ ] Todos los cálculos son auditables
- [ ] Los Pre_req forman cadenas lógicas (no circulares)
- [ ] Ordenado por Score_Real DESC
- [ ] Sesgos evaluados con razón documentada
- [ ] Comparativa completa vs roadmap anterior

---

## RESTRICCIONES FINALES

NO incluir:
- Actividades con Empleabilidad < 6 (después de ajustes)
- Actividades con Score_Real < 5.0
- Actividades con Red Flag activo
- Valores sin justificación

PRIORIZAR:
- Capa 1, 2, 3 sobre 4, 5
- Verificar GitHub stars para herramientas open source
- Cruzar fuentes: mínimo 2 menciones independientes
- Mostrar cálculo completo para cada Score_Real nuevo
- Datos verificados sobre estimaciones
