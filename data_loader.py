import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. Lectura directa
        df = pd.read_excel(file_path, sheet_name=sheet_target)

        # 2. Normalización de Nombres
        df.columns = df.columns.str.strip().str.capitalize() 
        
        # Mapeo de seguridad
        rename_map = {
            'Pre-req': 'Pre_req', 'Dependencia': 'Pre_req',
            'Prob': 'Probabilidad', 'Riesgo': 'Probabilidad',
            'Coste €': 'Coste', 'Score final': 'Score'
        }
        df = df.rename(columns=rename_map)

        # 3. Validación
        required_cols = ['Id', 'Actividad', 'Coste', 'Horas', 'Score', 'Pre_req', 'Probabilidad']
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            return pd.DataFrame(), pd.DataFrame()

        # 4. Limpieza
        df = df.dropna(subset=['Actividad'])
        
        cols_numeric = ['Id', 'Coste', 'Horas', 'Score', 'Pre_req', 'Probabilidad']
        for col in cols_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. Lógica de Negocio (Cálculos Avanzados)
        
        # A. Normalizar probabilidad (0-1)
        if df['Probabilidad'].max() > 1.5:
            df['Probabilidad'] = df['Probabilidad'] / 100.0

        # B. === LEADER RISK MITIGATION ===
        # Guardamos la original para auditoría
        df['Probabilidad_Original'] = df['Probabilidad']
        # Aplicamos la fórmula: El riesgo (1-Prob) se reduce a la mitad por Seniority
        df['Probabilidad'] = 1 - ((1 - df['Probabilidad_Original']) / 2)

        # C. Calcular Score Real (Con la probabilidad ajustada)
        df['Score_Real'] = df['Score'] * df['Probabilidad']
        
        # D. === EFICIENCIA BASADA EN TIEMPO (ROI por Hora) ===
        # Valor que obtengo por cada hora invertida.
        df['Eficiencia'] = np.where(df['Horas'] <= 0, 9999, df['Score_Real'] / df['Horas'])

        # Renombrar ID
        df = df.rename(columns={'Id': 'ID'})

        return df, df.copy()

    except Exception as e:
        st.error(f"Error leyendo el Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()