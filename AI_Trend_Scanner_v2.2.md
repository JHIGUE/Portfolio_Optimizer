# AI Trend Scanner v2.2

Prompt de investigación para generar/actualizar el dataset de actividades de upskilling.
Ejecutar en Claude con acceso a web search.

---

## CONTEXTO

Actúa como AI Research Analyst especializado en tendencias de upskilling para perfiles de Data & AI Leadership.

Mi perfil: Data & AI Leader | Head of Data | Architect & Strategist | Multi-Cloud (Azure/GCP/AWS) | Analytics & Governance

Mis fortalezas: SQL avanzado, Python, Power BI, arquitectura de datos, ETL/ELT, gobernanza de datos, gestión de stakeholders senior.

Fecha de ejecución: [HOY]

---

## REGLA CRÍTICA: DATOS OPERATIVOS

**NUNCA INVENTES Horas ni Coste.** Estos son datos factuales que deben venir de la URL oficial.

Para cada actividad:
1. Busca la URL oficial del curso/certificación/herramienta
2. Extrae Horas y Coste de esa fuente
3. Si no encuentras el dato exacto, marca como "VERIFICAR" y proporciona la URL

| Dato | Fuente autorizada | Puedes estimar? |
|------|-------------------|-----------------|
| Horas | URL oficial del curso | NO - Solo el dato real |
| Coste | URL oficial (pricing) | NO - Solo el dato real |
| Empleabilidad | Web search de job postings | SÍ - Basado en evidencia |
| Facilidad | Análisis de skills transferibles | SÍ - Basado en tu perfil |
| Capa_score | Taxonomía fija (ver abajo) | NO - Usar tabla |

---

## ROADMAP ACTUAL (INPUT)

Para actividades existentes, mantener Horas y Coste del Excel original a menos que la URL oficial muestre valores diferentes.

| ID | Actividad | Horas | Coste | URL_Fuente |
|----|-----------|-------|-------|------------|
| (completar con roadmap actual) |

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

**Para cada actividad nueva, buscar inmediatamente la URL oficial.**

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

## FASE 6: EXTRACCIÓN DE DATOS OPERATIVOS (NUEVO)

Para cada actividad, acceder a URL_Fuente y extraer:

### Horas
- Cursos: Duración oficial del curso
- Certificaciones: Tiempo de preparación recomendado
- Proyectos: Estimación conservadora basada en documentación

### Coste
- Cursos: Precio de inscripción (0 si gratuito)
- Certificaciones: Fee del examen
- Proyectos: 0 (a menos que requiera herramientas de pago)

**Si no encuentras el dato exacto:**
```
Horas: VERIFICAR (estimación: Xh)
Coste: VERIFICAR (estimación: X€)
URL: [la URL donde debería estar]
```

---

## FASE 7: EVALUACIÓN DE COMPONENTES ESTIMABLES

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

## FASE 8: CÁLCULO DE SCORES (AUDITABLE)

```
Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)

Prob_Acumulada:
- Si Pre_req = 0: Prob_Acum = Probabilidad
- Si Pre_req > 0: Prob_Acum = Probabilidad * Prob_Acum(actividad Pre_req)

Score_Real = Score_Base * Prob_Acum
```

MOSTRAR EL CÁLCULO COMPLETO para cada actividad.

---

## FASE 9: OUTPUT ESTRUCTURADO

### TABLA PRINCIPAL (con URL obligatoria)

| ID | Actividad | Tipo | Horas | Coste | Pre_req | Prob | Capa_id | Capa_desc | Capa_score | Empl | Facil | Score_Base | Prob_Acum | Score_Real | URL_Fuente |
|----|-----------|------|-------|-------|---------|------|---------|-----------|------------|------|-------|------------|-----------|------------|------------|

### ANÁLISIS DE SESGOS

| Actividad | HYPE | VENDOR | SURVIVORSHIP | Ajuste | Razón |
|-----------|------|--------|--------------|--------|-------|

### ACTIVIDADES DESCARTADAS

| Actividad | Red Flag | Motivo | URL |
|-----------|----------|--------|-----|

### DATOS A VERIFICAR

Lista de actividades donde Horas o Coste no pudieron confirmarse en la URL oficial.

### COMPARATIVA VS ROADMAP ANTERIOR

#### Actividades Nuevas
Para cada una: justificar clasificación, mostrar cálculo, citar URL

#### Actividades que Suben (delta >= 0.5)
ID | Actividad | Antes | Ahora | Componente que cambió | Por qué | URL evidencia

#### Actividades que Bajan (delta >= 0.5)
ID | Actividad | Antes | Ahora | Componente que cambió | Por qué | URL evidencia

### METADATA

```yaml
fecha_ejecucion: YYYY-MM-DD
fuentes_consultadas:
  - nombre: "..."
    url: "..."
    fecha_publicacion: "..."

estadisticas:
  actividades_total: X
  actividades_descartadas: X
  actividades_nuevas: X
  datos_verificados: X
  datos_pendientes_verificar: X
```

---

## VALIDACIÓN PRE-ENTREGA

Checklist:
- [ ] Todas las actividades tienen URL_Fuente
- [ ] Horas y Coste vienen de la URL, no estimados
- [ ] Actividades con datos no confirmados marcadas como VERIFICAR
- [ ] Sesgos evaluados con razón documentada
- [ ] Cálculos de Score son auditables
- [ ] Pre_req forman cadenas lógicas (no circulares)

---

## RESTRICCIONES FINALES

NO incluir:
- Actividades con Empleabilidad < 6 (después de ajustes)
- Actividades con Score_Real < 5.0
- Actividades con Red Flag activo
- Horas o Coste inventados sin URL de respaldo

PRIORIZAR:
- Capa 1, 2, 3 sobre 4, 5
- Datos verificables sobre estimaciones
- Múltiples fuentes sobre fuente única
