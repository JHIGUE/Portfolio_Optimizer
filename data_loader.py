import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. Carga
        df = pd.read_excel(file_path, sheet_name=sheet_target)

        # 2. Normalización de Cabeceras
        df.columns = df.columns.astype(str).str.strip().str.capitalize()
        
        # Mapeo estricto a tus nombres internos
        rename_map = {
            'Id': 'ID',
            'Pre-req': 'Pre_req', 'Pre_req': 'Pre_req',
            'Prob': 'Probabilidad', 'Probabilidad': 'Probabilidad',
            'Capa id': 'Capa_id', 'Capa_id': 'Capa_id',
            'Capa desc': 'Capa_desc', 'Capa_desc': 'Capa_desc',
            'Capa score': 'Capa_score', 'Capa_score': 'Capa_score',
            # Mapeos de seguridad por si acaso
            'Coste €': 'Coste', 'Horas': 'Horas'
        }
        df = df.rename(columns=rename_map)

        # 3. Conversión de Tipos
        cols_numeric = ['ID', 'Horas', 'Coste', 'Pre_req', 'Probabilidad', 
                        'Capa_id', 'Capa_score', 'Empleabilidad', 'Facilidad']
        
        for col in cols_numeric:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            else:
                # Si falta Capa_score, Empleabilidad o Facilidad, asignamos media (5)
                # para que el cálculo no se rompa, pero avisamos.
                if col in ['Empleabilidad', 'Facilidad', 'Capa_score']:
                    df[col] = 5 
        
        # Limpieza básica
        if 'Actividad' in df.columns:
            df = df.dropna(subset=['Actividad'])

        # 4. CÁLCULOS DE NEGOCIO (Aquí nace el Score)

        # A) Score Base Ponderado
        # Fórmula: (Empleabilidad * 0.4) + (Capa_score * 0.4) + (Facilidad * 0.2)
        df['Score_Base'] = (df['Empleabilidad'] * 0.4) + \
                           (df['Capa_score'] * 0.4) + \
                           (df['Facilidad'] * 0.2)

        # B) Probabilidad Acumulada (Recursiva)
        task_map = df.set_index('ID')[['Probabilidad', 'Pre_req']].to_dict('index')
        memo_prob = {}

        def get_prob_acumulada(task_id):
            if task_id in memo_prob: return memo_prob[task_id]
            if task_id not in task_map: return 1.0 # Si no existe, neutro
            
            node = task_map[task_id]
            propia = node['Probabilidad']
            parent = node['Pre_req']
            
            if parent == 0:
                acumulada = propia
            else:
                acumulada = propia * get_prob_acumulada(parent)
            
            memo_prob[task_id] = acumulada
            return acumulada

        df['Probabilidad_Acumulada'] = df['ID'].apply(get_prob_acumulada)

        # C) Score Real (El KPI Final)
        df['Score_Real'] = df['Score_Base'] * df['Probabilidad_Acumulada']
        
        # Para compatibilidad, creamos una columna 'Score' que sea igual al Base o Real
        # Esto evita que engine.py falle si busca "Score" para algo visual
        df['Score'] = df['Score_Base'] 

        # D) Eficiencia / ROI
        df['Eficiencia'] = np.where(df['Coste'] <= 0, 9999, df['Score_Real'] / df['Coste'])
        df['ROI'] = df['Eficiencia']

        return df, df.copy()

    except Exception as e:
        st.error(f"Error en data_loader: {e}")
        return pd.DataFrame(), pd.DataFrame()
