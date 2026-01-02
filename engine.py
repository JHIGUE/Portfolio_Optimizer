import pulp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import heapq

def run_optimization(df, budget, hours):
    # Mochila (Knapsack)
    prob = pulp.LpProblem("Opt", pulp.LpMaximize)
    rows = df.index.tolist()
    x = pulp.LpVariable.dicts("Sel", rows, cat='Binary')
    
    # Objetivo: Maximizar Score_Real (Ya calculado con probabilidad acumulada)
    prob += pulp.lpSum([df.loc[i, 'Score_Real'] * x[i] for i in rows])
    
    # Restricciones
    prob += pulp.lpSum([df.loc[i, 'Coste'] * x[i] for i in rows]) <= budget
    prob += pulp.lpSum([df.loc[i, 'Horas'] * x[i] for i in rows]) <= hours
    
    # Dependencias Topológicas
    if 'ID' in df.columns and 'Pre_req' in df.columns:
        id_map = dict(zip(df['ID'], df.index))
        for i in rows:
            pre = df.loc[i, 'Pre_req']
            if pre > 0 and pre in id_map:
                prob += x[i] <= x[id_map[pre]]

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return df.loc[[i for i in rows if x[i].varValue == 1]].copy()

def calculate_sequential_gantt(df_opt, weekly_hours):
    # (Misma lógica de Score Heredado que ya aprobaste - Se mantiene igual)
    if df_opt.empty: return pd.DataFrame()
    
    task_map = df_opt.set_index('ID').to_dict('index')
    children_map = {i: [] for i in df_opt['ID']}
    in_degree = {i: 0 for i in df_opt['ID']}
    
    for pid, row in task_map.items():
        pre = row['Pre_req']
        if pre > 0 and pre in task_map:
            children_map[pre].append(pid)
            in_degree[pid] += 1

    memo_effective_score = {}
    def get_effective_score(task_id):
        if task_id in memo_effective_score: return memo_effective_score[task_id]
        my_score = task_map[task_id]['Score_Real']
        max_child_potential = 0
        if children_map[task_id]:
            max_child_potential = max([get_effective_score(child) for child in children_map[task_id]])
        effective_score = max(my_score, max_child_potential)
        memo_effective_score[task_id] = effective_score
        return effective_score

    for pid in task_map: get_effective_score(pid)

    queue = []
    for pid, count in in_degree.items():
        if count == 0:
            heapq.heappush(queue, (-memo_effective_score[pid], pid))
            
    tasks = []
    end_dates_map = {} 
    resource_free_date = datetime(2026, 1, 1)
    
    while queue:
        eff_score_neg, pid = heapq.heappop(queue)
        row = task_map[pid]
        
        pre = row['Pre_req']
        earliest_start = datetime(2026, 1, 1)
        if pre > 0 and pre in end_dates_map:
            earliest_start = end_dates_map[pre] + timedelta(days=1)
            
        actual_start = max(earliest_start, resource_free_date)
        duration = max(1, int((row['Horas'] / weekly_hours) * 7))
        end_date = actual_start + timedelta(days=duration)
        
        end_dates_map[pid] = end_date
        resource_free_date = end_date 
        
        tasks.append({
            'Tarea': row['Actividad'], 'Inicio': actual_start, 'Fin': end_date, 
            'Tipo': row.get('Tipo', 'General'), 'ID': pid, 'Pre_req': pre,
            'Capa_desc': row.get('Capa_desc', 'General'), # Para colorear por capa si quieres
            'Prioridad_Calc': -eff_score_neg
        })
        
        for child_id in children_map[pid]:
            in_degree[child_id] -= 1
            if in_degree[child_id] == 0:
                heapq.heappush(queue, (-memo_effective_score[child_id], child_id))
                
    return pd.DataFrame(tasks)

def run_monte_carlo(df_plan, iterations=500):
    res = []
    # Usamos Score_Base porque si el evento "éxito" ocurre, te llevas el valor completo
    # Si usáramos Score_Real estaríamos penalizando dos veces por probabilidad
    val_col = 'Score_Base' if 'Score_Base' in df_plan.columns else 'Score_Real'
    
    for _ in range(iterations):
        t_factor = np.random.uniform(0.9, 1.5, size=len(df_plan))
        real_h = (df_plan['Horas'] * t_factor).sum()
        
        # Simulación de éxito basada en Probabilidad Individual (fallo puntual)
        success = np.random.random(size=len(df_plan)) < df_plan['Probabilidad'].values
        real_v = np.where(success, df_plan[val_col], 0).sum()
        
        res.append({'Horas': real_h, 'Valor': real_v})
    return pd.DataFrame(res)
