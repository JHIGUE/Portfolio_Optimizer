import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. Leemos el Excel tal cual
        df = pd.read_excel(file_path, sheet_name=sheet_target)
        
        # 2. Normalización de nombres de columnas (Todo a minúsculas y sin espacios extra)
        # Esto soluciona problemas como " Actividad " vs "Actividad" o "COSTE" vs "Coste"
        df.columns = df.columns.astype(str).str.strip().str.lower()
        
        # 3. Mapa de búsqueda inteligente
        # Buscamos qué columna real corresponde a nuestro concepto interno
        col_mapping = {}
        
        # Iteramos sobre las columnas reales del Excel
        for col_real in df.columns:
            # ID
            if col_real in ['id', '#', 'id_actividad']: 
                col_mapping['ID'] = col_real
            # Actividad
            elif 'actividad' in col_real: 
                col_mapping['Actividad'] = col_real
            # Coste (evitamos 'total')
            elif 'coste' in col_real and 'total' not in col_real: 
                col_mapping['Coste'] = col_real
            # Horas
            elif 'horas' in col_real: 
                col_mapping['Horas'] = col_real
            # Score
            elif 'score' in col_real and 'final' in col_real: # Prioridad Score Final
                col_mapping['Score'] = col_real
            elif 'score' in col_real and 'Score' not in col_mapping: # Fallback
                col_mapping['Score'] = col_real
            # Pre-requisito
            elif 'pre' in col_real and 'req' in col_real: 
                col_mapping['Pre_req'] = col_real
            elif 'dependencia' in col_real:
                col_mapping['Pre_req'] = col_real
            # Probabilidad
            elif 'prob' in col_real or 'riesgo' in col_real:
                col_mapping['Probabilidad'] = col_real
            # Tipo
            elif 'tipo' in col_real:
                col_mapping['Tipo'] = col_real

        # 4. Verificación de columnas críticas encontradas
        required_targets = ['ID', 'Actividad', 'Coste', 'Horas', 'Score']
        missing = [t for t in required_targets if t not in col_mapping]
        
        if missing:
            st.error(f"⚠️ Faltan columnas clave. El código buscó pero no encontró: {missing}")
            st.write("Columnas detectadas en tu Excel (normalizadas):", df.columns.tolist())
            return pd.DataFrame(), pd.DataFrame()

        # 5. Renombrado Estándar
        # Invertimos el mapa para renombrar: {nombre_feo: Nombre_Bonito}
        rename_map = {v: k for k, v in col_mapping.items()}
        df = df.rename(columns=rename_map)
        
        # 6. Limpieza y Tipos
        df = df.dropna(subset=['Actividad'])
        
        # Aseguramos columnas numéricas aunque vengan como texto
        for col in ['Coste', 'Horas', 'Score', 'ID']:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Tratamiento especial Pre_req (si no existe, creamos columna de ceros)
        if 'Pre_req' not in df.columns: df['Pre_req'] = 0
        else: df['Pre_req'] = pd.to_numeric(df['Pre_req'], errors='coerce').fillna(0)
            
        # Tratamiento especial Probabilidad
        if 'Probabilidad' not in df.columns: df['Probabilidad'] = 1.0
        else:
            df['Probabilidad'] = pd.to_numeric(df['Probabilidad'], errors='coerce').fillna(1.0)
            # Si detectamos porcentaje (ej: 90), pasamos a decimal (0.9)
            if df['Probabilidad'].max() > 1.5: df['Probabilidad'] /= 100.0

        # Tratamiento especial Tipo
        if 'Tipo' not in df.columns: df['Tipo'] = 'General'

        # 7. Cálculos Finales
        df['Score_Real'] = df['Score'] * df['Probabilidad']
        # Ratio eficiencia (9999 si es gratis)
        df['Eficiencia'] = np.where(df['Coste'] <= 0, 9999, df['Score_Real'] / df['Coste'])

        return df, df.copy()

    except Exception as e:
        st.error(f"Error crítico leyendo Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()
