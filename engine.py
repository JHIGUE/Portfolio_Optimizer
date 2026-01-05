import pulp
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import heapq

def run_optimization(df, hours, budget=None):
    """
    MOTOR DE OPTIMIZACIÓN (KNAPSACK PROBLEM)
    ----------------------------------------
    Selecciona el mejor conjunto de actividades que caben en el tiempo disponible.
    """
    # 1. Crear el problema de maximización
    prob = pulp.LpProblem("Opt", pulp.LpMaximize)
    rows = df.index.tolist()
    
    # 2. Variables de decisión (Binarias: 1 = Hago la tarea, 0 = No la hago)
    x = pulp.LpVariable.dicts("Sel", rows, cat='Binary')
    
    # 3. Función Objetivo: Maximizar la suma de 'Score_Real'
    prob += pulp.lpSum([df.loc[i, 'Score_Real'] * x[i] for i in rows])
    
    # 4. Restricciones
    
    # A. Restricción de TIEMPO (Obligatoria: Tu cuello de botella)
    prob += pulp.lpSum([df.loc[i, 'Horas'] * x[i] for i in rows]) <= hours
    
    # B. Restricción de PRESUPUESTO (Opcional: Solo si activaste el checkbox)
    if budget is not None:
        prob += pulp.lpSum([df.loc[i, 'Coste'] * x[i] for i in rows]) <= budget
    
    # C. Restricción de DEPENDENCIAS (Integridad Referencial)
    # Si la tarea 'Hijo' se selecciona (x=1), la tarea 'Padre' DEBE seleccionarse (x=1).
    # Matemáticamente: x[hijo] <= x[padre]
    if 'ID' in df.columns and 'Pre_req' in df.columns:
        id_map = dict(zip(df['ID'], df.index))
        for i in rows:
            pre_id = df.loc[i, 'Pre_req']
            # Solo si tiene un prerrequisito válido que existe en el Excel
            if pre_id > 0 and pre_id in id_map:
                padre_idx = id_map[pre_id]
                prob += x[i] <= x[padre_idx]

    # 5. Resolver
    prob.solve(pulp.PULP_CBC_CMD(msg=0))
    
    # 6. Devolver resultado
    selected_indices = [i for i in rows if x[i].varValue == 1]
    return df.loc[selected_indices].copy()


def calculate_sequential_gantt(df_opt, weekly_hours):
    """
    MOTOR DE CALENDARIZACIÓN (TOPOLOGICAL SORT + HEAP)
    --------------------------------------------------
    Ordena las tareas óptimas en una línea de tiempo realista.
    Usa 'Score Heredado' para priorizar desbloqueadores.
    """
    if df_opt.empty: return pd.DataFrame()
    
    # 1. Mapeo de Grafos (Relaciones Padre-Hijo)
    task_map = df_opt.set_index('ID').to_dict('index')
    children_map = {i: [] for i in df_opt['ID']} # Quién depende de mí
    in_degree = {i: 0 for i in df_opt['ID']}     # De cuántos dependo yo
    
    for pid, row in task_map.items():
        pre = row['Pre_req']
        if pre > 0 and pre in task_map:
            children_map[pre].append(pid)
            in_degree[pid] += 1

    # 2. Cálculo de "Score Heredado" (Back-Propagation)
    # Una tarea pequeña necesaria para una grande hereda la importancia de la grande.
    memo_effective_score = {}

    def get_effective_score(task_id):
        if task_id in memo_effective_score: return memo_effective_score[task_id]
        
        my_score = task_map[task_id]['Score_Real']
        # Miro el potencial de mis hijos recursivamente
        max_child_potential = 0
        if children_map[task_id]:
            max_child_potential = max([get_effective_score(child) for child in children_map[task_id]])
        
        # Valgo lo que valgo yo, O lo que vale mi hijo más importante (el mayor de los dos)
        effective_score = max(my_score, max_child_potential)
        memo_effective_score[task_id] = effective_score
        return effective_score

    # Pre-calentamos el score para todas las tareas
    for pid in task_map: get_effective_score(pid)

    # 3. Cola de Prioridad (Heap)
    # Metemos las tareas que NO tienen dependencias pendientes (in_degree 0)
    queue = []
    for pid, count in in_degree.items():
        if count == 0:
            # Usamos negativo porque python heapq es min-heap (queremos sacar el score más alto)
            heapq.heappush(queue, (-memo_effective_score[pid], pid))
            
    # 4. Bucle Principal de Asignación
    tasks = []
    end_dates_map = {} 
    # Fecha de inicio: Primer lunes laboral de 2026
    resource_free_date = datetime(2026, 1, 5) 
    
    while queue:
        # Sacamos la mejor tarea disponible
        _, pid = heapq.heappop(queue)
        row = task_map[pid]
        
        # Calculamos cuándo puede empezar
        pre = row['Pre_req']
        earliest_start_by_dep = datetime(2026, 1, 5)
        
        # A. Restricción de Dependencia: No antes de que acabe el padre
        if pre > 0 and pre in end_dates_map:
            earliest_start_by_dep = end_dates_map[pre] + timedelta(days=1)
            
        # B. Restricción de Recurso: No antes de que TÚ estés libre
        actual_start = max(earliest_start_by_dep, resource_free_date)
        
        # Calculamos duración (semanas -> días)
        duration = max(1, int((row['Horas'] / max(1, weekly_hours)) * 7))
        end_date = actual_start + timedelta(days=duration)
        
        # Actualizamos estado del sistema
        end_dates_map[pid] = end_date
        resource_free_date = end_date 
        
        # Guardamos la tarea
        tasks.append({
            'Tarea': row['Actividad'], 
            'Inicio': actual_start, 
            'Fin': end_date, 
            'Tipo': row.get('Tipo', 'General'), 
            'ID': pid, 
            'Pre_req': pre,
            'Capa_desc': row.get('Capa_desc', 'General')
        })
        
        # 5. Desbloqueo de Hijos
        # Ahora que he terminado esta tarea, aviso a mis hijos
        for child_id in children_map[pid]:
            in_degree[child_id] -= 1
            # Si un hijo ya no tiene dependencias pendientes, entra a la cola
            if in_degree[child_id] == 0:
                heapq.heappush(queue, (-memo_effective_score[child_id], child_id))
                
    return pd.DataFrame(tasks)


def run_monte_carlo(df_plan, iterations=500):
    """
    SIMULACIÓN DE RIESGO (MONTE CARLO)
    ----------------------------------
    Evalúa qué tan probable es cumplir el plan.
    """
    res = []
    # Usamos Score_Real (que ya tiene el ajuste de riesgo de Líder)
    val_col = 'Score_Real' 
    
    for _ in range(iterations):
        # 1. Incertidumbre de Tiempo (Ley de Hofstadter: siempre tardas más)
        # Multiplicador aleatorio entre 0.9 (90% del tiempo est.) y 1.5 (150%)
        t_factor = np.random.uniform(0.9, 1.5, size=len(df_plan))
        real_h = (df_plan['Horas'] * t_factor).sum()
        
        # 2. Incertidumbre de Éxito (Bernoulli)
        # Tiramos el dado basado en la Probabilidad de la tarea
        success = np.random.random(size=len(df_plan)) < df_plan['Probabilidad'].values
        
        # Si éxito=True sumamos valor, si no, 0.
        real_v = np.where(success, df_plan[val_col], 0).sum()
        
        res.append({'Horas': real_h, 'Valor': real_v})
        
    return pd.DataFrame(res)