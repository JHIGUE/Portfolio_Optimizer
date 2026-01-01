import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. Escaneo inteligente de cabecera
        df_scan = pd.read_excel(file_path, sheet_name=sheet_target, header=None, nrows=20)
        header_idx = None
        for i, row in df_scan.iterrows():
            s = row.astype(str).str.lower().tolist()
            if any('tipo' in x for x in s) and any('coste' in x for x in s):
                header_idx = i
                break
        
        if header_idx is None: return pd.DataFrame()

        # 2. Lectura real
        df_raw = pd.read_excel(file_path, sheet_name=sheet_target, header=header_idx)
        
        # 3. Mapeo de columnas (Búsqueda por palabras clave)
        cols = {}
        for idx, col_name in enumerate(df_raw.columns):
            c = str(col_name).lower().strip()
            if c in ['#', 'id', 'id_actividad'] and 'id' not in cols: cols['id'] = idx
            elif 'actividad' in c: cols['actividad'] = idx
            elif 'tipo' in c: cols['tipo'] = idx
            elif 'horas' in c: cols['horas'] = idx
            elif 'coste' in c and 'total' not in c: cols['coste'] = idx
            elif 'score' in c and 'final' in c: cols['score'] = idx
            elif 'score' in c and 'roi' in c and 'score' not in cols: cols['score'] = idx
            elif 'pre_req' in c or 'dependencia' in c: cols['pre_req'] = idx
            elif 'prob' in c or 'riesgo' in c: cols['prob'] = idx

        df = pd.DataFrame()
        def ext(k, n): 
            if k in cols: df[n] = df_raw.iloc[:, cols[k]]
        
        ext('actividad', 'Actividad')
        ext('id', 'ID')
        ext('tipo', 'Tipo')
        ext('horas', 'Horas')
        ext('coste', 'Coste')
        ext('score', 'Score')
        ext('pre_req', 'Pre_req')
        ext('prob', 'Probabilidad')

        if 'Actividad' in df.columns: df = df.dropna(subset=['Actividad'])
        
        # Limpieza numérica
        for c in ['Horas', 'Coste', 'Score', 'ID', 'Pre_req', 'Probabilidad']:
            if c in df.columns: df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0)

        # Lógica de negocio (Probabilidad y Score Real)
        if 'Probabilidad' not in df.columns: df['Probabilidad'] = 1.0
        else:
            df['Probabilidad'] = df['Probabilidad'].replace(0, 1.0)
            if df['Probabilidad'].max() > 1.5: df['Probabilidad'] /= 100.0
        
        if 'Score' in df.columns: 
            df['Score_Real'] = df['Score'] * df['Probabilidad']
            # Ratio visual para auditoría
            df['Eficiencia'] = np.where(df['Coste'] <= 0, 999999, df['Score_Real'] / df['Coste'])

        return df, df_raw # Devolvemos limpio y crudo (para auditoría)
    except Exception as e:
        st.error(f"Error en data_loader: {e}")
        return pd.DataFrame(), pd.DataFrame()