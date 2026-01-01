import pulp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def run_optimization(df, budget, hours):
    # Algoritmo de la Mochila (Knapsack)
    prob = pulp.LpProblem("Opt", pulp.LpMaximize)
    rows = df.index.tolist()
    x = pulp.LpVariable.dicts("Sel", rows, cat='Binary')
    
    sc_col = 'Score_Real' if 'Score_Real' in df.columns else 'Score'
    
    prob += pulp.lpSum([df.loc[i, sc_col] * x[i] for i in rows])
    prob += pulp.lpSum([df.loc[i, 'Coste'] * x[i] for i in rows]) <= budget
    prob += pulp.lpSum([df.loc[i, 'Horas'] * x[i] for i in rows]) <= hours
    
    if 'ID' in df.columns and 'Pre_req' in df.columns:
        id_map = dict(zip(df['ID'], df.index))
        for i in rows:
            pre = df.loc[i, 'Pre_req']
            if pre > 0 and pre in id_map:
                prob += x[i] <= x[id_map[pre]]

    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    return df.loc[[i for i in rows if x[i].varValue == 1]].copy()

def calculate_sequential_gantt(df_opt, weekly_hours):
    if df_opt.empty: return pd.DataFrame()
    
    # --- 1. PREPARACIÓN DE DATOS ---
    task_map = df_opt.set_index('ID').to_dict('index')
    # Mapa de Hijos: {Padre -> [Lista de Hijos]}
    children_map = {i: [] for i in df_opt['ID']}
    in_degree = {i: 0 for i in df_opt['ID']} # Contador de padres pendientes
    
    for pid, row in task_map.items():
        pre = row['Pre_req']
        if pre > 0 and pre in task_map:
            children_map[pre].append(pid)
            in_degree[pid] += 1

    # --- 2. CÁLCULO DEL "SCORE HEREDADO" (LA CLAVE DE TU LÓGICA) ---
    # Una tarea hereda el Score de sus hijos si este es mayor que el suyo propio.
    # Usamos recursividad con memoria (memoization) para propagar desde el nieto al abuelo.
    
    memo_effective_score = {}

    def get_effective_score(task_id):
        if task_id in memo_effective_score:
            return memo_effective_score[task_id]
        
        # Mi valor base
        my_score = task_map[task_id]['Score_Real']
        
        # Calculamos el valor máximo que puedo desbloquear (mis hijos)
        max_child_potential = 0
        if children_map[task_id]:
            # Recursivamente buscamos el mejor score aguas abajo
            max_child_potential = max([get_effective_score(child) for child in children_map[task_id]])
        
        # Mi prioridad real es el mayor entre MI valor y el de mi MEJOR descendiente
        effective_score = max(my_score, max_child_potential)
        
        memo_effective_score[task_id] = effective_score
        return effective_score

    # Calculamos el score efectivo para todas las tareas
    for pid in task_map:
        get_effective_score(pid)

    # --- 3. COLA DE PRIORIDAD ---
    # Ahora el algoritmo usa el 'effective_score', no el 'Score_Real' original.
    import heapq
    queue = []
    
    # Inicializamos con las tareas que no tienen bloqueo (padres = 0)
    for pid, count in in_degree.items():
        if count == 0:
            # Prioridad: -Score_Heredado (para que sea Max-Heap)
            heapq.heappush(queue, (-memo_effective_score[pid], pid))
            
    # --- 4. CONSTRUCCIÓN DEL GANTT ---
    tasks = []
    end_dates_map = {} 
    resource_free_date = datetime(2026, 1, 1)
    
    while queue:
        # Sacamos la tarea con mayor "Potencial Estratégico"
        eff_score_neg, pid = heapq.heappop(queue)
        row = task_map[pid]
        
        # Cálculo de fechas (igual que antes)
        pre = row['Pre_req']
        earliest_start_by_dep = datetime(2026, 1, 1)
        
        if pre > 0 and pre in end_dates_map:
            earliest_start_by_dep = end_dates_map[pre] + timedelta(days=1)
            
        actual_start = max(earliest_start_by_dep, resource_free_date)
        duration = max(1, int((row['Horas'] / weekly_hours) * 7))
        end_date = actual_start + timedelta(days=duration)
        
        end_dates_map[pid] = end_date
        resource_free_date = end_date 
        
        tasks.append({
            'Tarea': row['Actividad'], 
            'Inicio': actual_start, 
            'Fin': end_date, 
            'Tipo': row.get('Tipo', 'General'), 
            'ID': pid, 
            'Pre_req': pre,
            # Guardamos el score heredado para que lo veas en el hover del gráfico
            'Prioridad_Calc': -eff_score_neg 
        })
        
        # Desbloqueamos hijos
        for child_id in children_map[pid]:
            in_degree[child_id] -= 1
            if in_degree[child_id] == 0:
                heapq.heappush(queue, (-memo_effective_score[child_id], child_id))
                
    return pd.DataFrame(tasks)

def run_monte_carlo(df_plan, iterations=500):
    res = []
    for _ in range(iterations):
        t_factor = np.random.uniform(0.9, 1.5, size=len(df_plan))
        real_h = (df_plan['Horas'] * t_factor).sum()
        success = np.random.random(size=len(df_plan)) < df_plan['Probabilidad'].values
        real_v = np.where(success, df_plan['Score'], 0).sum()
        res.append({'Horas': real_h, 'Valor': real_v})

    return pd.DataFrame(res)
