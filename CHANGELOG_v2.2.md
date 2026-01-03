# Changelog

All notable changes to SPO (Strategic Portfolio Optimizer) are documented here.

## [2.2.0] - 2026-01-03

### Added
- **Verificación de datos:** Horas y Coste deben extraerse de URL oficial o fuentes web contrastadas
- **Columna URL_Fuente:** Cada actividad tiene URL para verificar datos operativos
- **Sección "Datos pendientes de verificar":** Lista actividades con datos marcados "VERIFICAR"
- **Time-First Model:** Horas es la restricción principal, Presupuesto es opcional
- **Curva de Valor:** Nueva visualización de sensibilidad temporal

### Changed
- **IDs secuenciales:** Actividades nuevas usan IDs numéricos consecutivos (no "NEW*")
- **Esquema de datos:** 12 columnas obligatorias en el output del prompt
- **Prompt v2.2:** Basado en v2.1 con reglas de verificación añadidas
- `engine.py`: `run_optimization(df, hours, budget=None)` - budget ahora es opcional
- Sidebar: Checkbox para activar/desactivar límite de presupuesto

### Removed
- Mapa de Calor bidimensional (redundante con modelo Time-First)
- "Frontera de Pareto" mal nombrada (era curva de eficiencia)

---

## [2.1.0] - 2026-01-02

### Added
- Bias Detection System: 3 tipos de sesgo (Hype, Vendor, Survivorship)
- Red Flags Filtering: Descarte automático por GitHub <1K stars, fuente única
- Taxonomía de Capas: 5 niveles estratégicos (Orchestration > Infrastructure)
- Auditoría estadística completa

### Changed
- Fórmula de Score: `Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)`
- Probabilidad propaga por cadenas de dependencias

---

## [2.0.0] - 2025-12-28

### Added
- Monte Carlo Simulation: Análisis de riesgo con 500 iteraciones
- Gantt con Score Heredado: Back-propagation de prioridad
- Comparador de escenarios

### Changed
- Migración de ROI ranking a Knapsack optimization (PuLP)
- UI restructurada en pestañas

---

## [1.0.0] - 2025-12-15

### Added
- Release inicial
- Dashboard Streamlit básico
- Input manual desde Excel
- Ordenación por ROI (greedy)

---

## Versioning

Semantic Versioning:
- MAJOR: Cambios breaking en formato de datos o lógica de algoritmo
- MINOR: Nuevas features, backward compatible
- PATCH: Bug fixes
