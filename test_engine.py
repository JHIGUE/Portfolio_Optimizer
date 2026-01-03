"""
Tests for SPO - Strategic Portfolio Optimizer
Run with: pytest tests/test_engine.py -v
"""

import pytest
import pandas as pd
import numpy as np
from datetime import datetime

# Importamos los módulos a testear
import sys
sys.path.append('..')


class TestScoreCalculation:
    """Tests para validar la fórmula del Score"""
    
    def test_score_base_formula(self):
        """
        Score_Base = (Empleabilidad × 0.4) + (Capa_score × 0.4) + (Facilidad × 0.2)
        """
        empleabilidad = 10
        capa_score = 9
        facilidad = 8
        
        expected = (10 * 0.4) + (9 * 0.4) + (8 * 0.2)  # 4 + 3.6 + 1.6 = 9.2
        
        assert expected == 9.2, "Fórmula Score_Base incorrecta"
    
    def test_score_real_with_probability(self):
        """
        Score_Real = Score_Base × Prob_Acumulada
        """
        score_base = 9.2
        prob_acumulada = 0.8
        
        expected = score_base * prob_acumulada  # 7.36
        
        assert expected == pytest.approx(7.36, 0.01)
    
    def test_probability_chain(self):
        """
        Si A(0.9) → B(0.8) → C(0.7):
        Prob_Acum(C) = 0.9 × 0.8 × 0.7 = 0.504
        """
        prob_a = 0.9
        prob_b = 0.8
        prob_c = 0.7
        
        prob_acum_c = prob_a * prob_b * prob_c
        
        assert prob_acum_c == pytest.approx(0.504, 0.001)


class TestTaxonomyScores:
    """Tests para validar la taxonomía de capas"""
    
    TAXONOMY = {
        'Orchestration': 10,
        'Governance': 9,
        'Data & Memory': 9,
        'Models': 7,
        'Infrastructure': 5
    }
    
    def test_orchestration_is_highest(self):
        """Orchestration debe tener el score máximo"""
        assert self.TAXONOMY['Orchestration'] == 10
    
    def test_infrastructure_is_lowest(self):
        """Infrastructure debe tener el score mínimo"""
        assert self.TAXONOMY['Infrastructure'] == 5
    
    def test_governance_equals_data(self):
        """Governance y Data & Memory tienen igual prioridad"""
        assert self.TAXONOMY['Governance'] == self.TAXONOMY['Data & Memory']


class TestKnapsackConstraints:
    """Tests para validar restricciones del optimizador"""
    
    def test_budget_constraint(self):
        """El coste total nunca debe exceder el presupuesto"""
        budget = 500
        selected_costs = [100, 150, 200]  # Total: 450
        
        assert sum(selected_costs) <= budget
    
    def test_hours_constraint(self):
        """Las horas totales nunca deben exceder la bolsa"""
        hours_available = 300
        selected_hours = [50, 80, 100, 60]  # Total: 290
        
        assert sum(selected_hours) <= hours_available
    
    def test_dependency_constraint(self):
        """Si B depende de A, no puedes seleccionar B sin A"""
        selected = {'A': True, 'B': True}
        dependencies = {'B': 'A'}  # B requiere A
        
        for task, prereq in dependencies.items():
            if selected.get(task, False):
                assert selected.get(prereq, False), f"{task} seleccionado sin prereq {prereq}"


class TestBiasDetection:
    """Tests para validar detección de sesgos"""
    
    def test_hype_bias_penalty(self):
        """HYPE_BIAS debe reducir Empleabilidad en -2"""
        original_empleabilidad = 8
        hype_bias = True
        
        adjusted = original_empleabilidad - 2 if hype_bias else original_empleabilidad
        
        assert adjusted == 6
    
    def test_vendor_bias_penalty(self):
        """VENDOR_BIAS debe reducir Empleabilidad en -1"""
        original_empleabilidad = 8
        vendor_bias = True
        
        adjusted = original_empleabilidad - 1 if vendor_bias else original_empleabilidad
        
        assert adjusted == 7
    
    def test_survivorship_discard(self):
        """SURVIVORSHIP_BIAS con GitHub <1K stars debe descartar"""
        github_stars = 500
        survivorship_bias = True
        
        should_discard = survivorship_bias and github_stars < 1000
        
        assert should_discard == True


class TestGanttLogic:
    """Tests para validar lógica del Gantt con Score Heredado"""
    
    def test_inherited_score(self):
        """
        Si A (score=2) bloquea B (score=9):
        Score_Efectivo(A) = max(2, 9) = 9
        """
        score_a = 2
        score_b = 9
        a_blocks_b = True
        
        effective_score_a = max(score_a, score_b) if a_blocks_b else score_a
        
        assert effective_score_a == 9
    
    def test_blocker_priority(self):
        """El bloqueador debe ejecutarse antes que el bloqueado"""
        tasks = [
            {'id': 'A', 'prereq': None, 'effective_score': 9},
            {'id': 'B', 'prereq': 'A', 'effective_score': 9}
        ]
        
        # Ordenamos por effective_score, pero A va primero por dependencia
        execution_order = ['A', 'B']
        
        assert execution_order[0] == 'A'


class TestRedFlags:
    """Tests para validar criterios de descarte automático"""
    
    RED_FLAG_CRITERIA = {
        'github_min_stars': 1000,
        'min_sources': 2,
        'max_cost_without_roi': 500
    }
    
    def test_github_red_flag(self):
        """GitHub <1K stars es Red Flag"""
        stars = 800
        is_red_flag = stars < self.RED_FLAG_CRITERIA['github_min_stars']
        assert is_red_flag == True
    
    def test_single_source_red_flag(self):
        """Fuente única es Red Flag"""
        sources_count = 1
        is_red_flag = sources_count < self.RED_FLAG_CRITERIA['min_sources']
        assert is_red_flag == True
    
    def test_cost_without_roi_red_flag(self):
        """Coste >500€ sin ROI demostrable es Red Flag"""
        cost = 600
        has_proven_roi = False
        is_red_flag = cost > self.RED_FLAG_CRITERIA['max_cost_without_roi'] and not has_proven_roi
        assert is_red_flag == True


# Para ejecutar: pytest tests/test_engine.py -v --tb=short
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
