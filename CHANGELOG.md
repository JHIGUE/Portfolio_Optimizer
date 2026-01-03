# Changelog

All notable changes to SPO (Strategic Portfolio Optimizer) are documented here.

## [2.1.0] - 2026-01-03

### Added
- **Bias Detection System**: Prompt now evaluates 3 types of bias (Hype, Vendor, Survivorship) with automatic score adjustments
- **Red Flags Filtering**: Automatic discard of activities with GitHub <1K stars, single source, or minor vendor certifications
- **Traceability**: Every Score_Real calculation is now auditable with component breakdown
- **Taxonomía de Capas**: 5-tier strategic classification (Orchestration → Infrastructure)

### Changed
- Score formula updated: `Score_Base = (Empleabilidad × 0.4) + (Capa_score × 0.4) + (Facilidad × 0.2)`
- Probability now propagates through dependency chains (`Prob_Acumulada`)

### Removed
- Generic "Valor" column replaced by explicit `Score_Base` and `Score_Real`

---

## [2.0.0] - 2025-12-28

### Added
- **Monte Carlo Simulation**: Risk analysis with 500 iterations
- **Pareto Frontier**: Full budget range visualization (0€ to max)
- **Gantt with Score Heredado**: Back-propagation of priority through dependencies
- **Scenario Comparator**: Save and compare multiple budget configurations
- **Context Tab**: Manifest explaining algorithm logic to end users

### Changed
- Migrated from simple ROI ranking to Knapsack optimization (PuLP)
- UI restructured into 8 tabs for better separation of concerns

### Technical
- Refactored into 3 modules: `app.py`, `data_loader.py`, `engine.py`

---

## [1.0.0] - 2025-12-15

### Added
- Initial release
- Basic Streamlit dashboard
- Manual Excel input
- ROI-based sorting (greedy approach)

---

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Breaking changes to data format or algorithm logic
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes
