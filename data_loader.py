import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. Lectura directa
        df = pd.read_excel(file_path, sheet_name=sheet_target)

        # 2. Normalización de Nombres (Limpieza básica)
        df.columns = df.columns.str.strip().str.capitalize() 
        
        # Mapeo de seguridad para variantes de nombres comunes
        rename_map = {
            'Pre-req': 'Pre_req', 'Dependencia': 'Pre_req',
            'Prob': 'Probabilidad', 'Riesgo': 'Probabilidad',
            'Coste €': 'Coste', 'Score final': 'Score',
            'Capa_score': 'Capa_score', 'Empleabilidad': 'Empleabilidad', 'Facilidad': 'Facilidad'
        }
        df = df.rename(columns=rename_map)

        # 3. Lógica de "Auto-Cálculo" del Score (EL FIX)
        # Si el Excel no trae 'Score' calculado, lo calculamos nosotros con los ingredientes.
        if 'Score' not in df.columns:
            # Verificamos si tenemos los ingredientes necesarios
            ingredientes = ['Empleabilidad', 'Capa_score', 'Facilidad']
            if all(col in df.columns for col in ingredientes):
                # Fórmula: 40% Empleabilidad + 40% Capa + 20% Facilidad
                df['Score'] = (df['Empleabilidad'] * 0.4) + \
                              (df['Capa_score'] * 0.4) + \
                              (df['Facilidad'] * 0.2)
            else:
                # Si no hay Score ni ingredientes, fallará en la validación siguiente
                pass

        # 4. Validación de Columnas Mínimas
        # Ahora 'Score' ya debería existir (o venir del Excel o calculado arriba)
        required_cols = ['Id', 'Actividad', 'Coste', 'Horas', 'Score', 'Pre_req', 'Probabilidad']
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            st.error(f"Faltan columnas clave en el Excel: {missing}")
            return pd.DataFrame(), pd.DataFrame()

        # 5. Limpieza de Datos
        df = df.dropna(subset=['Actividad'])
        
        cols_numeric = ['Id', 'Coste', 'Horas', 'Score', 'Pre_req', 'Probabilidad']
        for col in cols_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 6. Lógica de Negocio Avanzada (Leader Risk & Time-First)
        
        # A. Normalizar probabilidad (0-1) si viene en formato 0-100
        if df['Probabilidad'].max() > 1.5:
            df['Probabilidad'] = df['Probabilidad'] / 100.0

        # B. === LEADER RISK MITIGATION ===
        # Guardamos original para auditoría
        df['Probabilidad_Original'] = df['Probabilidad']
        # Fórmula: Prob_Adj = 1 - (Riesgo / 2) -> Seniority reduce el riesgo a la mitad
        df['Probabilidad'] = 1 - ((1 - df['Probabilidad_Original']) / 2)

        # C. Calcular Score Real (Valor ajustado al riesgo)
        df['Score_Real'] = df['Score'] * df['Probabilidad']
        
        # D. === EFICIENCIA BASADA EN TIEMPO (ROI por Hora) ===
        # Evitamos división por cero poniendo un valor muy alto (9999) si horas es 0
        df['Eficiencia'] = np.where(df['Horas'] <= 0, 9999, df['Score_Real'] / df['Horas'])

        # Renombrar ID para consistencia interna del engine
        df = df.rename(columns={'Id': 'ID'})

        return df, df.copy()

    except Exception as e:
        st.error(f"Error técnico leyendo el Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()