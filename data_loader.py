import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. EL RADAR: Leemos las primeras 20 filas "a ciegas"
        df_scan = pd.read_excel(file_path, sheet_name=sheet_target, header=None, nrows=20)
        
        header_row_index = None
        
        # Buscamos la fila que tenga las palabras "actividad" y "coste"
        for i, row in df_scan.iterrows():
            row_text = row.astype(str).str.lower().tolist()
            if any('actividad' in x for x in row_text) and any('coste' in x for x in row_text):
                header_row_index = i
                break
        
        if header_row_index is None:
            # Si falla el radar, probamos la fila 0 por defecto
            header_row_index = 0

        # 2. LECTURA OFICIAL: Leemos usando la fila detectada
        df = pd.read_excel(file_path, sheet_name=sheet_target, header=header_row_index)
        
        # 3. NORMALIZACIÓN (Hacerlo robusto a mayúsculas/minúsculas)
        df.columns = df.columns.astype(str).str.strip().str.lower()
        
        col_mapping = {}
        for col_real in df.columns:
            if col_real in ['id', '#', 'id_actividad']: col_mapping['ID'] = col_real
            elif 'actividad' in col_real: col_mapping['Actividad'] = col_real
            elif 'coste' in col_real: col_mapping['Coste'] = col_real
            elif 'horas' in col_real: col_mapping['Horas'] = col_real
            elif 'score' in col_real: col_mapping['Score'] = col_real
            elif 'pre' in col_real or 'dependencia' in col_real: col_mapping['Pre_req'] = col_real
            elif 'prob' in col_real or 'riesgo' in col_real: col_mapping['Probabilidad'] = col_real
            elif 'tipo' in col_real: col_mapping['Tipo'] = col_real

        # 4. RENOMBRADO
        rename_map = {v: k for k, v in col_mapping.items()}
        df = df.rename(columns=rename_map)
        
        # 5. LIMPIEZA
        if 'Actividad' in df.columns:
            df = df.dropna(subset=['Actividad'])
        
        for col in ['Coste', 'Horas', 'Score', 'ID']:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        if 'Pre_req' not in df.columns: df['Pre_req'] = 0
        else: df['Pre_req'] = pd.to_numeric(df['Pre_req'], errors='coerce').fillna(0)
            
        if 'Probabilidad' not in df.columns: df['Probabilidad'] = 1.0
        else:
            df['Probabilidad'] = pd.to_numeric(df['Probabilidad'], errors='coerce').fillna(1.0)
            if df['Probabilidad'].max() > 1.5: df['Probabilidad'] /= 100.0
            
        if 'Tipo' not in df.columns: df['Tipo'] = 'General'

        # Cálculos finales
        if 'Score' in df.columns and 'Coste' in df.columns:
            df['Score_Real'] = df['Score'] * df['Probabilidad']
            df['Eficiencia'] = np.where(df['Coste'] <= 0, 9999, df['Score_Real'] / df['Coste'])
            return df, df.copy()
            
        return pd.DataFrame(), pd.DataFrame()

    except Exception as e:
        # Este mensaje te dirá si el archivo no existe realmente
        st.error(f"Error cargando Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()
