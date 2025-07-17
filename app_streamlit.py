import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import seaborn as sns

# Configuración de la página
st.set_page_config(
    page_title="Análisis de Desplazamiento y Precipitación",
    page_icon="📊",
    layout="wide"
)

# Título principal
st.title("📊 Análisis de Desplazamiento y Precipitación")
st.markdown("---")

# Función para cargar y procesar datos
@st.cache_data
def load_data(uploaded_file):
    """Carga y procesa los datos del archivo CSV"""
    try:
        # Leer el archivo CSV con separador de punto y coma
        df = pd.read_csv(uploaded_file, sep=';', encoding='utf-8')
        
        # Limpiar el DataFrame
        df = df.dropna(how='all')  # Eliminar filas completamente vacías
        
        # Detectar si es el formato específico del usuario
        if 'fecha' in df.columns:
            # Formato específico del usuario
            df = process_user_format(df)
        else:
            # Formato estándar
            df = process_standard_format(df)
        
        if df is None:
            return None
        
        # Ordenar por fecha
        df = df.sort_values('Date')
        
        # Calcular desplazamiento acumulado
        df['Cumulative_Displacement'] = df['Displacement'].cumsum()
        
        return df
    except Exception as e:
        st.error(f"Error al cargar el archivo: {str(e)}")
        return None

def process_user_format(df):
    """Procesa el formato específico del usuario"""
    try:
        # Eliminar las primeras filas que contienen metadatos
        df = df[df.iloc[:, 0].notna() & (df.iloc[:, 0] != 'fecha')]
        
        # Encontrar donde están los datos numéricos
        numeric_rows = df[pd.to_numeric(df.iloc[:, 0], errors='coerce').notna()]
        
        if numeric_rows.empty:
            st.error("No se encontraron datos numéricos válidos")
            return None
        
        # Extraer las columnas necesarias
        dates_excel = pd.to_numeric(numeric_rows.iloc[:, 0], errors='coerce')
        
        # Buscar la columna de precipitación (la que tiene valores más altos)
        precipitation_col = None
        for col in numeric_rows.columns:
            col_data = pd.to_numeric(numeric_rows[col], errors='coerce')
            if col_data.notna().any() and col_data.max() > 10:  # Precipitación típicamente > 10mm
                precipitation_col = col
                break
        
        if precipitation_col is None:
            st.error("No se pudo identificar la columna de precipitación")
            return None
        
        # Usar la primera columna de desplazamiento (después de la fecha)
        displacement_col = numeric_rows.columns[1]
        
        # Convertir fechas de Excel a datetime
        dates = pd.to_datetime(dates_excel - 25569, unit='D', origin='1900-01-01')
        
        # Crear DataFrame limpio
        clean_df = pd.DataFrame({
            'Date': dates,
            'Displacement': pd.to_numeric(numeric_rows[displacement_col], errors='coerce'),
            'Precipitation': pd.to_numeric(numeric_rows[precipitation_col], errors='coerce')
        })
        
        # Eliminar filas con datos faltantes
        clean_df = clean_df.dropna()
        
        return clean_df
        
    except Exception as e:
        st.error(f"Error procesando formato del usuario: {str(e)}")
        return None

def process_standard_format(df):
    """Procesa el formato estándar"""
    try:
        # Verificar que tenga las columnas necesarias
        required_columns = ['Date', 'Displacement', 'Precipitation']
        if not all(col in df.columns for col in required_columns):
            st.error(f"El archivo debe contener las columnas: {required_columns}")
            return None
        
        # Convertir fecha a datetime
        df['Date'] = pd.to_datetime(df['Date'])
        
        return df
        
    except Exception as e:
        st.error(f"Error procesando formato estándar: {str(e)}")
        return None

# Función para crear la gráfica principal
def create_main_plot(df):
    """Crea la gráfica principal con desplazamiento y precipitación"""
    
    # Crear subplots con doble eje Y
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    # Gráfica de desplazamiento acumulado (puntos)
    fig.add_trace(
        go.Scatter(
            x=df['Date'],
            y=df['Cumulative_Displacement'],
            mode='markers',
            name='Desplazamiento Acumulado',
            marker=dict(
                color='blue',
                size=6,
                symbol='circle'
            ),
            yaxis='y'
        ),
        secondary_y=False,
    )
    
    # Gráfica de precipitación (barras)
    fig.add_trace(
        go.Bar(
            x=df['Date'],
            y=df['Precipitation'],
            name='Precipitación',
            marker=dict(color='orange'),
            opacity=0.7,
            yaxis='y2'
        ),
        secondary_y=True,
    )
    
    # Configurar ejes
    fig.update_xaxes(title_text="Fecha")
    fig.update_yaxes(title_text="Desplazamiento (cm)", secondary_y=False)
    fig.update_yaxes(title_text="Precipitación Mensual (mm)", secondary_y=True)
    
    # Configurar layout
    fig.update_layout(
        title="Desplazamiento Acumulado vs Precipitación",
        hovermode='x unified',
        height=600,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    return fig

# Función para calcular estadísticas
def calculate_statistics(df):
    """Calcula estadísticas descriptivas"""
    stats = {
        'Desplazamiento Total': df['Cumulative_Displacement'].iloc[-1],
        'Desplazamiento Promedio por Periodo': df['Displacement'].mean(),
        'Velocidad Media (cm/día)': df['Displacement'].mean() / 30,  # Asumiendo periodos mensuales
        'Precipitación Total': df['Precipitation'].sum(),
        'Precipitación Promedio': df['Precipitation'].mean(),
        'Máximo Desplazamiento en un Periodo': df['Displacement'].max(),
        'Máxima Precipitación en un Periodo': df['Precipitation'].max(),
        'Fecha con Mayor Desplazamiento': df.loc[df['Displacement'].idxmax(), 'Date'].strftime('%Y-%m-%d'),
        'Fecha con Mayor Precipitación': df.loc[df['Precipitation'].idxmax(), 'Date'].strftime('%Y-%m-%d')
    }
    return stats

# Función para crear histograma de precipitaciones
def create_precipitation_histogram(df):
    """Crea un histograma de precipitaciones mensuales"""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Crear histograma
    n, bins, patches = ax.hist(df['Precipitation'], bins=15, alpha=0.7, color='skyblue', edgecolor='black')
    
    # Configurar el gráfico
    ax.set_xlabel('Precipitación (mm)')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Distribución de Precipitaciones Mensuales')
    ax.grid(True, alpha=0.3)
    
    # Añadir estadísticas al gráfico
    mean_precip = df['Precipitation'].mean()
    median_precip = df['Precipitation'].median()
    ax.axvline(mean_precip, color='red', linestyle='--', linewidth=2, label=f'Media: {mean_precip:.1f} mm')
    ax.axvline(median_precip, color='green', linestyle='--', linewidth=2, label=f'Mediana: {median_precip:.1f} mm')
    ax.legend()
    
    return fig

# Interfaz principal
def main():
    # Sidebar para carga de archivo
    st.sidebar.header("📂 Carga de Datos")
    uploaded_file = st.sidebar.file_uploader(
        "Sube tu archivo CSV",
        type=['csv'],
        help="El archivo debe contener las columnas: Date, Displacement, Precipitation"
    )
    
    if uploaded_file is not None:
        # Cargar datos
        df = load_data(uploaded_file)
        
        if df is not None:
            # Mostrar información básica
            st.sidebar.success(f"✅ Archivo cargado correctamente")
            st.sidebar.info(f"📊 Registros: {len(df)}")
            st.sidebar.info(f"📅 Periodo: {df['Date'].min().strftime('%Y-%m-%d')} a {df['Date'].max().strftime('%Y-%m-%d')}")
            
            # Filtros
            st.sidebar.header("🔍 Filtros")
            
            # Filtro por rango de fechas
            min_date = df['Date'].min().date()
            max_date = df['Date'].max().date()
            
            date_range = st.sidebar.date_input(
                "Selecciona rango de fechas",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
            
            # Aplicar filtro de fechas
            if len(date_range) == 2:
                start_date, end_date = date_range
                df_filtered = df[(df['Date'].dt.date >= start_date) & (df['Date'].dt.date <= end_date)]
            else:
                df_filtered = df
            
            # Contenido principal
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.subheader("📈 Gráfica Principal")
                
                # Mostrar gráfica principal
                fig = create_main_plot(df_filtered)
                st.plotly_chart(fig, use_container_width=True)
                
            with col2:
                st.subheader("📊 Estadísticas")
                
                # Calcular y mostrar estadísticas
                stats = calculate_statistics(df_filtered)
                
                for key, value in stats.items():
                    if isinstance(value, float):
                        st.metric(key, f"{value:.2f}")
                    else:
                        st.metric(key, value)
            
            # Funcionalidades adicionales
            st.markdown("---")
            st.subheader("🔧 Análisis Adicional")
            
            # Tabs para diferentes análisis
            tab1, tab2, tab3 = st.tabs(["📊 Tabla de Datos", "📈 Histograma", "📋 Resumen Estadístico"])
            
            with tab1:
                st.subheader("Datos Filtrados")
                st.dataframe(df_filtered, use_container_width=True)
                
                # Opción para descargar datos filtrados
                csv = df_filtered.to_csv(index=False)
                st.download_button(
                    label="📥 Descargar datos filtrados",
                    data=csv,
                    file_name='datos_filtrados.csv',
                    mime='text/csv'
                )
            
            with tab2:
                st.subheader("Distribución de Precipitaciones")
                fig_hist = create_precipitation_histogram(df_filtered)
                st.pyplot(fig_hist)
            
            with tab3:
                st.subheader("Resumen Estadístico Detallado")
                
                # Estadísticas de desplazamiento
                st.write("**Desplazamiento:**")
                displacement_stats = df_filtered['Displacement'].describe()
                st.dataframe(displacement_stats.to_frame().T)
                
                # Estadísticas de precipitación
                st.write("**Precipitación:**")
                precipitation_stats = df_filtered['Precipitation'].describe()
                st.dataframe(precipitation_stats.to_frame().T)
                
                # Correlación
                correlation = df_filtered['Displacement'].corr(df_filtered['Precipitation'])
                st.metric("Correlación Desplazamiento-Precipitación", f"{correlation:.3f}")
    
    else:
        # Mostrar instrucciones cuando no hay archivo
        st.info("👆 Sube un archivo CSV para comenzar el análisis")
        
        # Mostrar ejemplo de formato de datos
        st.subheader("📝 Formato de Datos Requerido")
        st.write("Tu archivo CSV debe tener la siguiente estructura:")
        
        example_data = {
            'Date': ['2023-01-01', '2023-02-01', '2023-03-01', '2023-04-01'],
            'Displacement': [0.5, 1.2, 0.8, 1.5],
            'Precipitation': [45, 78, 32, 95]
        }
        st.dataframe(pd.DataFrame(example_data))
        
        st.write("""
        **Descripción de columnas:**
        - **Date**: Fecha en formato YYYY-MM-DD
        - **Displacement**: Desplazamiento en el periodo (cm)
        - **Precipitation**: Precipitación mensual (mm)
        
        **Nota:** La aplicación también puede procesar archivos con formato de Excel que usen:
        - Separador de punto y coma (;)
        - Fechas en formato numérico de Excel
        - Múltiples columnas de desplazamiento (tomará la primera)
        """)

        # Mostrar información sobre el archivo subido
        st.subheader("ℹ️ Información sobre tu archivo")
        st.write("""
        **Tu archivo actual tiene:**
        - Separador: punto y coma (;)
        - Fechas en formato Excel (números como 42338, 42362...)
        - Múltiples columnas de desplazamiento
        - Columna de precipitación
        
        La aplicación procesará automáticamente este formato y:
        1. Convertirá las fechas Excel a formato estándar
        2. Seleccionará la primera columna de desplazamiento
        3. Identificará automáticamente la columna de precipitación
        """)

        # Mostrar preview de cómo se verán los datos
        st.subheader("📊 Vista previa de datos procesados")
        preview_data = {
            'Date': ['2015-12-01', '2015-12-25', '2016-01-18', '2016-02-11'],
            'Displacement': [0.0395, -0.0882, 0.003, 0.0604],
            'Precipitation': [18.73, 28.95, 51.91, 78.53]
        }
        st.dataframe(pd.DataFrame(preview_data))

if __name__ == "__main__":
    main()