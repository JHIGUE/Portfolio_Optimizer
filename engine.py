import pulp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import heapq

def run_optimization(df, hours, budget=None):
    """
    Ejecuta el algoritmo Knapsack (Mochila).
    - Objetivo: Maximizar 'Score_Real'.
    - Restricción Dura: 'Horas' <= hours.
    - Restricción Opcional: 'Coste' <= budget (solo si budget no es None).
    - Restricción Dependencia: Si elijo B, debo elegir A (Pre_req).
    """
    # 1. Definición del Problema
    prob = pulp.LpProblem("Opt", pulp.LpMaximize)
    rows = df.index.tolist()
    
    # Variables de decisión (1 si selecciono la actividad, 0 si no)
    x = pulp.LpVariable.dicts("Sel", rows, cat='Binary')
    
    # 2. Función Objetivo: Maximizar Valor Estratégico Real
    prob += pulp.lpSum([df.loc[i, 'Score_Real'] * x[i] for i in rows])
    
    # 3. Restricciones
    # A. Tiempo (El recurso crítico)
    prob += pulp.lpSum([df.loc[i, 'Horas'] * x[i] for i in rows]) <= hours
    
    # B. Presupuesto (Solo si el usuario activó el límite)
    if budget is not None:
        prob += pulp.lpSum([df.loc[i, 'Coste'] * x[i] for i in rows]) <= budget
    
    # C. Dependencias Topológicas (Si B requiere A, y hago B, entonces A=1)
    # Lógica: x[hijo] <= x[padre] -> Si hijo=1, padre fuerza a ser 1.
    if 'ID' in df.columns and 'Pre_req' in df.columns:
        # Mapa para buscar índices por ID real
        id_map = dict(zip(df['ID'], df.index))
        
        for i in rows:
            pre_id = df.loc[i, 'Pre_req']
            # Si tiene prerrequisito y ese prerrequisito existe en los datos
            if pre_id > 0 and pre_id in id_map:
                padre_idx = id_map[pre_id]
                prob += x[i] <= x[padre_idx]

    # 4. Resolución
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # Retornamos solo las filas seleccionadas
    selected_indices = [i for i in rows if x[i].varValue == 1]
    return df.loc[selected_indices].copy()


def calculate_sequential_gantt(df_opt, weekly_hours):
    """
    Genera un cronograma inteligente usando 'Score Heredado'.
    Prioriza tareas que desbloquean alto valor futuro.
    """
    if df_opt.empty: return pd.DataFrame()
    
    # --- 1. PREPARACIÓN DE GRAFO ---
    task_map = df_opt.set_index('ID').to_dict('index')
    # Mapa de Hijos: {Padre -> [Lista de Hijos]}
    children_map = {i: [] for i in df_opt['ID']}
    in_degree = {i: 0 for i in df_opt['ID']} # Cuántos padres pendientes tiene
    
    for pid, row in task_map.items():
        pre = row['Pre_req']
        if pre > 0 and pre in task_map:
            children_map[pre].append(pid)
            in_degree[pid] += 1

    # --- 2. CÁLCULO DEL "SCORE HEREDADO" ---
    # Una tarea hereda el valor de sus hijos si es mayor que el suyo propio.
    # Esto asegura que los prerrequisitos de tareas importantes se hagan pronto.
    memo_effective_score = {}

    def get_effective_score(task_id):
        if task_id in memo_effective_score:
            return memo_effective_score[task_id]
        
        my_score = task_map[task_id]['Score_Real']
        
        # Valor máximo que puedo desbloquear (mis hijos)
        max_child_potential = 0
        if children_map[task_id]:
            max_child_potential = max([get_effective_score(child) for child in children_map[task_id]])
        
        # Mi valor efectivo es MAX(Mi Valor, Valor de mi mejor descendiente)
        effective_score = max(my_score, max_child_potential)
        
        memo_effective_score[task_id] = effective_score
        return effective_score

    # Pre-calculamos para todos
    for pid in task_map:
        get_effective_score(pid)

    # --- 3. COLA DE PRIORIDAD ---
    # Usamos heap (cola de prioridad) para elegir siempre la mejor tarea disponible
    queue = []
    
    # Inicializamos con tareas sin dependencias (in_degree 0)
    for pid, count in in_degree.items():
        if count == 0:
            # Guardamos negativo porque heapq es min-heap (queremos el mayor score primero)
            heapq.heappush(queue, (-memo_effective_score[pid], pid))
            
    # --- 4. CONSTRUCCIÓN DEL CRONOGRAMA ---
    tasks = []
    end_dates_map = {} 
    # Empezamos el primer lunes de 2026 (o fecha arbitraria)
    resource_free_date = datetime(2026, 1, 5) 
    
    while queue:
        # Sacamos la tarea más prioritaria
        eff_score_neg, pid = heapq.heappop(queue)
        row = task_map[pid]
        
        # Cálculo de fechas
        pre = row['Pre_req']
        earliest_start_by_dep = datetime(2026, 1, 5)
        
        # Si tiene padre, no puede empezar antes de que acabe el padre
        if pre > 0 and pre in end_dates_map:
            earliest_start_by_dep = end_dates_map[pre] + timedelta(days=1) # +1 día de descanso/gap
            
        # Además, no puede empezar antes de que TÚ estés libre
        actual_start = max(earliest_start_by_dep, resource_free_date)
        
        # Duración en días naturales (asumiendo trabajo semanal)
        weeks_needed = row['Horas'] / max(1, weekly_hours)
        days_needed = int(weeks_needed * 7)
        duration = max(1, days_needed)
        
        end_date = actual_start + timedelta(days=duration)
        
        # Actualizamos estado
        end_dates_map[pid] = end_date
        resource_free_date = end_date 
        
        tasks.append({
            'Tarea': row['Actividad'], 
            'Inicio': actual_start, 
            'Fin': end_date, 
            'Tipo': row.get('Tipo', 'General'), 
            'ID': pid, 
            'Pre_req': pre,
            'Capa_desc': row.get('Capa_desc', 'General'), # Para colorear por capa
            'Prioridad_Calc': -eff_score_neg # Para debug en el hover
        })
        
        # Desbloqueamos hijos
        for child_id in children_map[pid]:
            in_degree[child_id] -= 1
            if in_degree[child_id] == 0:
                heapq.heappush(queue, (-memo_effective_score[child_id], child_id))
                
    return pd.DataFrame(tasks)


def run_monte_carlo(df_plan, iterations=500):
    """
    Simulación de Riesgos:
    1. Incertidumbre en Tiempo (Factor aleatorio de horas).
    2. Incertidumbre en Éxito (Probabilidad de completar/aprobar).
    """
    res = []
    # Determinamos qué columna usar como 'Valor' base para sumar
    # Usamos Score_Base porque el riesgo ya lo simulamos aquí con el dado
    val_col = 'Score_Base' if 'Score_Base' in df_plan.columns else 'Score_Real'
    
    for _ in range(iterations):
        # A. Incertidumbre de Estimación (Hofstadter's Law: siempre tarda más)
        # Factor entre 0.9 (fuiste rápido) y 1.5 (se complicó)
        t_factor = np.random.uniform(0.9, 1.5, size=len(df_plan))
        real_h = (df_plan['Horas'] * t_factor).sum()
        
        # B. Incertidumbre de Éxito (Bernoulli Trial)
        # Tiramos un dado para cada tarea basado en su Probabilidad
        success = np.random.random(size=len(df_plan)) < df_plan['Probabilidad'].values
        
        # Si éxito = 1, sumamos valor. Si no, 0.
        real_v = np.where(success, df_plan[val_col], 0).sum()
        
        res.append({'Horas': real_h, 'Valor': real_v})
        
    return pd.DataFrame(res)