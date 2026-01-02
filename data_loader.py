import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. Carga de Datos
        df = pd.read_excel(file_path, sheet_name=sheet_target)

        # 2. Normalización de Cabeceras (Strip y Capitalize para consistencia)
        df.columns = df.columns.astype(str).str.strip().str.capitalize()
        
        # Mapeo de seguridad para garantizar nombres internos
        # Aseguramos que 'Capa_score' se lea correctamente aunque venga como 'Capa score'
        rename_map = {
            'Id': 'ID',
            'Pre-req': 'Pre_req',
            'Pre_req': 'Pre_req', # Por si acaso
            'Prob': 'Probabilidad',
            'Capa id': 'Capa_id',
            'Capa_id': 'Capa_id',
            'Capa desc': 'Capa_desc',
            'Capa_desc': 'Capa_desc',
            'Capa score': 'Capa_score',
            'Capa_score': 'Capa_score'
        }
        df = df.rename(columns=rename_map)

        # 3. Conversión de Tipos (Sanitización)
        cols_numeric = ['ID', 'Horas', 'Coste', 'Pre_req', 'Probabilidad', 
                        'Capa_id', 'Capa_score', 'Empleabilidad', 'Facilidad']
        
        for col in cols_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                # Si falta alguna columna crítica del nuevo modelo, avisamos o rellenamos
                if col in ['Empleabilidad', 'Facilidad', 'Capa_score']:
                    df[col] = 5 # Valor medio por defecto para no romper el cálculo
        
        # 4. LÓGICA DE NEGOCIO (Tus Peticiones)

        # A) SCORE BASE
        # Fórmula: (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)
        df['Score_Base'] = (df['Empleabilidad'] * 0.4) + \
                           (df['Capa_score'] * 0.4) + \
                           (df['Facilidad'] * 0.2)

        # B) PROBABILIDAD ACUMULADA (Recursividad)
        # Creamos un diccionario para acceso rápido: ID -> {Probabilidad, Pre_req}
        task_map = df.set_index('ID')[['Probabilidad', 'Pre_req']].to_dict('index')
        memo_prob = {} # Memoria para no recalcular ramas repetidas

        def get_prob_acumulada(task_id):
            # Si ya lo calculé, devuélvelo (Memoization)
            if task_id in memo_prob:
                return memo_prob[task_id]
            
            # Si el ID no existe (ej. Pre_req=0), asumimos probabilidad 1 (sin riesgo externo)
            if task_id not in task_map:
                return 1.0
            
            node = task_map[task_id]
            propia = node['Probabilidad']
            parent = node['Pre_req']
            
            # Caso Base: No tiene padre (Pre_req es 0)
            if parent == 0:
                acumulada = propia
            else:
                # Caso Recursivo: Mi Prob * Prob Acumulada de mi Padre
                acumulada = propia * get_prob_acumulada(parent)
            
            memo_prob[task_id] = acumulada
            return acumulada

        # Aplicamos la función recursiva a cada fila
        df['Probabilidad_Acumulada'] = df['ID'].apply(get_prob_acumulada)

        # C) SCORE REAL (El KPI final para el Optimizador)
        # Valor ajustado al riesgo real de la cadena
        df['Score_Real'] = df['Score_Base'] * df['Probabilidad_Acumulada']

        # D) EFICIENCIA / ROI
        # Evitamos división por cero. Si coste es 0, eficiencia es muy alta (9999)
        df['Eficiencia'] = np.where(df['Coste'] <= 0, 9999, df['Score_Real'] / df['Coste'])
        df['ROI'] = df['Eficiencia'] # Alias para visualización

        return df, df.copy()

    except Exception as e:
        st.error(f"Error crítico en data_loader: {e}")
        return pd.DataFrame(), pd.DataFrame()
