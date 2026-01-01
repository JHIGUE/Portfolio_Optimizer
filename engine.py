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
    tasks = []
    end_dates_map = {} 
    resource_free_date = datetime(2026, 1, 1)
    
    # Ordenación por Dependencia > Score > ID
    df_sorted = df_opt.sort_values(by=['Pre_req', 'Score_Real', 'ID'], ascending=[True, False, True])
    rows_pending = df_sorted.to_dict('records')
    processed_count = 0
    max_loops = len(rows_pending) * 5 
    
    while rows_pending and processed_count < max_loops:
        row = rows_pending.pop(0)
        processed_count += 1
        pid = row['ID']
        pre = row['Pre_req']
        
        earliest_start = datetime(2026, 1, 1)
        if pre > 0:
            if pre in end_dates_map: earliest_start = end_dates_map[pre] + timedelta(days=1)
            elif pre in df_opt['ID'].values:
                rows_pending.append(row)
                continue
            else: pass

        actual_start = max(earliest_start, resource_free_date)
        duration = max(1, int((row['Horas'] / weekly_hours) * 7))
        end_date = actual_start + timedelta(days=duration)
        
        end_dates_map[pid] = end_date
        resource_free_date = end_date 
        
        tasks.append({'Tarea': row['Actividad'], 'Inicio': actual_start, 'Fin': end_date, 'Tipo': row.get('Tipo','G'), 'ID': pid, 'Pre_req': pre})
        
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