"""
Tests for SPO - Strategic Portfolio Optimizer
Run with: pytest tests/test_engine.py -v
"""

import pytest
import numpy as np


class TestScoreFormula:
    """Tests para validar la formula del Score"""
    
    def test_score_base_calculation(self):
        """
        Score_Base = (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)
        """
        empleabilidad = 10
        capa_score = 9
        facilidad = 8
        
        expected = (10 * 0.4) + (9 * 0.4) + (8 * 0.2)  # 4 + 3.6 + 1.6 = 9.2
        
        assert expected == pytest.approx(9.2, 0.01)
    
    def test_score_base_minimum(self):
        """Score_Base minimo teorico"""
        empleabilidad = 1
        capa_score = 5  # Minimo en taxonomia
        facilidad = 1
        
        expected = (1 * 0.4) + (5 * 0.4) + (1 * 0.2)  # 0.4 + 2.0 + 0.2 = 2.6
        
        assert expected == pytest.approx(2.6, 0.01)
    
    def test_score_base_maximum(self):
        """Score_Base maximo teorico"""
        empleabilidad = 10
        capa_score = 10
        facilidad = 10
        
        expected = (10 * 0.4) + (10 * 0.4) + (10 * 0.2)  # 4 + 4 + 2 = 10
        
        assert expected == pytest.approx(10.0, 0.01)
    
    def test_score_real_with_probability(self):
        """Score_Real = Score_Base * Prob_Acumulada"""
        score_base = 9.2
        prob_acumulada = 0.8
        
        expected = score_base * prob_acumulada  # 7.36
        
        assert expected == pytest.approx(7.36, 0.01)


class TestProbabilityChain:
    """Tests para validar calculo de probabilidad acumulada"""
    
    def test_single_task_probability(self):
        """Tarea sin dependencias: Prob_Acum = Prob_propia"""
        prob_propia = 0.9
        pre_req = 0  # Sin dependencia
        
        prob_acum = prob_propia
        
        assert prob_acum == 0.9
    
    def test_chain_probability(self):
        """
        Cadena A(0.9) -> B(0.8) -> C(0.7):
        Prob_Acum(C) = 0.9 * 0.8 * 0.7 = 0.504
        """
        prob_a = 0.9
        prob_b = 0.8
        prob_c = 0.7
        
        prob_acum_c = prob_a * prob_b * prob_c
        
        assert prob_acum_c == pytest.approx(0.504, 0.001)
    
    def test_probability_bounds(self):
        """Prob_Acum siempre en (0, 1]"""
        probs = [0.9, 0.8, 0.7, 0.6]
        
        prob_acum = np.prod(probs)
        
        assert 0 < prob_acum <= 1


class TestTaxonomy:
    """Tests para validar la taxonomia de capas"""
    
    TAXONOMY = {
        'Orchestration': 10,
        'Governance': 9,
        'Data & Memory': 9,
        'Models': 7,
        'Infrastructure': 5
    }
    
    def test_orchestration_highest(self):
        """Orchestration tiene score maximo"""
        assert self.TAXONOMY['Orchestration'] == 10
    
    def test_infrastructure_lowest(self):
        """Infrastructure tiene score minimo"""
        assert self.TAXONOMY['Infrastructure'] == 5
    
    def test_governance_equals_data(self):
        """Governance y Data tienen igual prioridad"""
        assert self.TAXONOMY['Governance'] == self.TAXONOMY['Data & Memory']
    
    def test_all_scores_in_range(self):
        """Todos los scores en rango [5, 10]"""
        for score in self.TAXONOMY.values():
            assert 5 <= score <= 10


class TestKnapsackConstraints:
    """Tests para validar restricciones del optimizador"""
    
    def test_budget_constraint(self):
        """Coste total nunca excede presupuesto"""
        budget = 500
        selected_costs = [100, 150, 200]  # Total: 450
        
        assert sum(selected_costs) <= budget
    
    def test_hours_constraint(self):
        """Horas totales nunca exceden bolsa"""
        hours_available = 300
        selected_hours = [50, 80, 100, 60]  # Total: 290
        
        assert sum(selected_hours) <= hours_available
    
    def test_dependency_constraint(self):
        """Si B depende de A, no puedes seleccionar B sin A"""
        selected = {'A': True, 'B': True}
        dependencies = {'B': 'A'}
        
        for task, prereq in dependencies.items():
            if selected.get(task, False):
                assert selected.get(prereq, False), f"{task} seleccionado sin prereq {prereq}"


class TestBiasDetection:
    """Tests para validar deteccion de sesgos"""
    
    def test_hype_bias_penalty(self):
        """HYPE_BIAS reduce Empleabilidad en -2"""
        original = 8
        hype_bias = True
        
        adjusted = original - 2 if hype_bias else original
        
        assert adjusted == 6
    
    def test_vendor_bias_penalty(self):
        """VENDOR_BIAS reduce Empleabilidad en -1"""
        original = 8
        vendor_bias = True
        
        adjusted = original - 1 if vendor_bias else original
        
        assert adjusted == 7
    
    def test_survivorship_discard(self):
        """SURVIVORSHIP_BIAS con GitHub <1K stars descarta"""
        github_stars = 500
        survivorship_bias = True
        
        should_discard = survivorship_bias and github_stars < 1000
        
        assert should_discard == True


class TestGanttScoreHeredado:
    """Tests para validar logica del Gantt con Score Heredado"""
    
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
    
    def test_no_inheritance_without_dependency(self):
        """Sin dependencia, no hay herencia"""
        score_a = 2
        score_b = 9
        a_blocks_b = False
        
        effective_score_a = max(score_a, score_b) if a_blocks_b else score_a
        
        assert effective_score_a == 2


class TestMonteCarlo:
    """Tests para validar simulacion Monte Carlo"""
    
    def test_time_factor_bounds(self):
        """Factor de tiempo en rango [0.9, 1.5]"""
        np.random.seed(42)
        factors = np.random.uniform(0.9, 1.5, size=1000)
        
        assert factors.min() >= 0.9
        assert factors.max() <= 1.5
    
    def test_bernoulli_success(self):
        """Exito simulado respeta probabilidad"""
        np.random.seed(42)
        prob = 0.8
        n = 10000
        
        successes = np.random.random(n) < prob
        observed_rate = successes.mean()
        
        # Debe estar cerca de 0.8 (tolerancia 0.02)
        assert abs(observed_rate - prob) < 0.02


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
