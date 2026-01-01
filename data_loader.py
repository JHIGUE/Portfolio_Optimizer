import pandas as pd
import numpy as np
import streamlit as st

@st.cache_data
def load_data(file_path, sheet_target):
    try:
        # 1. Lectura directa (Sin buscar cabeceras raras)
        # Asumimos que la fila 0 tiene los títulos correctos
        df = pd.read_excel(file_path, sheet_name=sheet_target)

        # 2. Normalización de Nombres (Por si acaso escribes "coste" o "Coste")
        df.columns = df.columns.str.strip().str.capitalize() # Convierte "coste" -> "Coste"
        
        # Mapeo de seguridad para nombres variantes
        rename_map = {
            'Pre-req': 'Pre_req', 'Dependencia': 'Pre_req',
            'Prob': 'Probabilidad', 'Riesgo': 'Probabilidad',
            'Coste €': 'Coste', 'Score final': 'Score'
        }
        df = df.rename(columns=rename_map)

        # 3. Validación de Columnas Mínimas
        required_cols = ['Id', 'Actividad', 'Coste', 'Horas', 'Score', 'Pre_req', 'Probabilidad']
        missing = [c for c in required_cols if c not in df.columns]
        
        if missing:
            # Intentamos arreglar mayúsculas/minúsculas antes de fallar
            # Si falla, devolvemos vacío para que la App no explote
            return pd.DataFrame(), pd.DataFrame()

        # 4. Limpieza de Datos
        df = df.dropna(subset=['Actividad']) # Borrar filas vacías
        
        cols_numeric = ['Id', 'Coste', 'Horas', 'Score', 'Pre_req', 'Probabilidad']
        for col in cols_numeric:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        # 5. Lógica de Negocio (Cálculos)
        # Normalizar probabilidad (si viene en % como 90, pasarlo a 0.9)
        if df['Probabilidad'].max() > 1.5:
            df['Probabilidad'] = df['Probabilidad'] / 100.0
            
        # Calcular Score Real (Valor esperado)
        df['Score_Real'] = df['Score'] * df['Probabilidad']
        
        # Calcular Eficiencia (Para gráficos)
        # Si Coste es 0, ponemos un valor alto (9999) para que salga primero
        df['Eficiencia'] = np.where(df['Coste'] <= 0, 9999, df['Score_Real'] / df['Coste'])

        # Renombrar ID a mayúsculas para que el engine lo encuentre
        df = df.rename(columns={'Id': 'ID'})

        return df, df.copy() # Devolvemos lo mismo (limpio) dos veces para compatibilidad

    except Exception as e:
        st.error(f"Error leyendo el Excel: {e}")
        return pd.DataFrame(), pd.DataFrame()
