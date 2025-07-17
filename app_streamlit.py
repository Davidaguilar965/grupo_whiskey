import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

# Título de la app
st.title("Análisis de Desplazamiento y Precipitación - Gráfica Dual con Anotaciones")

# Carga de datos
uploaded_file = st.file_uploader(
    "Sube el archivo CSV con datos de desplazamiento y precipitación", 
    type=["csv"]
)

if uploaded_file:
    # Leer CSV delimitado por comas y eliminar BOM si existiera
    df = pd.read_csv(
        uploaded_file,
        sep=',',
        encoding='utf-8-sig',
        engine='python'
    )

    # Limpieza de nombres de columna
    df.columns = df.columns.str.strip()
    df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

    # Convertir y ordenar fechas
    df['fecha'] = pd.to_datetime(df['fecha'], dayfirst=True, errors='coerce')
    df = df.dropna(subset=['fecha'])
    df.sort_values('fecha', inplace=True)
    df.reset_index(drop=True, inplace=True)

    # Vista previa de los datos
    st.subheader("Vista previa de datos")
    st.dataframe(df.head())

    # Definir columna de precipitación
    precip_col = 'rainfall(mm)'
    if precip_col not in df.columns:
        st.error(f"No se encontró la columna '{precip_col}' en el CSV.")
    else:
        # Columnas de desplazamiento: todas excepto 'fecha' y precipitación
        disp_cols = [c for c in df.columns if c not in ['fecha', precip_col]]
        disp_cols = sorted(disp_cols, key=lambda x: int(x))

        # Validaciones
        errores = []
        if df['fecha'].isna().all():
            errores.append("La columna 'fecha' no se pudo convertir a datetime.")
        if not disp_cols:
            errores.append("No se encontraron columnas de desplazamiento.")
        if errores:
            for err in errores:
                st.error(err)
        else:
            # Gráfica dual
            fig, ax = plt.subplots(figsize=(12, 6))
            ax2 = ax.twinx()

            # Precipitación
            y_precip = df[precip_col]
            ax2.plot(df['fecha'], y_precip, label='rainfall (mm)', linewidth=2, marker='o')
            for xi, yi in zip(df['fecha'], y_precip):
                if pd.notna(yi):
                    ax2.annotate(f"{yi:.1f}", (xi, yi), textcoords='offset points', xytext=(0,5), ha='center', fontsize='x-small')

            # Desplazamientos
            for col in disp_cols:
                ax.scatter(df['fecha'], df[col], s=40, label=col)

            # Estilo
            ax.set_xlabel('Fecha')
            ax.set_ylabel('Desplazamiento (cm)')
            ax2.set_ylabel('Precipitación mensual (mm)')
            ax.grid(True, linestyle='--', linewidth=0.5)
            ax.xaxis.set_major_locator(mdates.AutoDateLocator())
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
            fig.autofmt_xdate(rotation=45)
            h1, l1 = ax.get_legend_handles_labels()
            h2, l2 = ax2.get_legend_handles_labels()
            ax.legend(h1+h2, l1+l2, loc='upper left', fontsize='small', ncol=3)
            st.pyplot(fig)

            # --- Funciones adicionales ---
            # 1. Fecha con mayor tasa de desplazamiento
            deltas = df[disp_cols].diff()
            delta_t = df['fecha'].diff().dt.total_seconds() / (24*3600)
            tasa = deltas.div(delta_t, axis=0)
            tasa_prom = tasa.mean(axis=1)
            idx_max = tasa_prom.idxmax()
            fecha_tasa = df.loc[idx_max, 'fecha']
            valor_tasa = tasa_prom.max()
            st.subheader("Fecha con mayor tasa de desplazamiento")
            st.write(f"La mayor tasa media diaria se registró el {fecha_tasa.date()} ({valor_tasa:.3f} cm/día).")

            # 2. Tabla resumen de estadísticas descriptivas
            st.subheader("Tabla resumen de estadísticas descriptivas")
            estadisticas = df[disp_cols + [precip_col]].describe()
            st.dataframe(estadisticas)
else:
    st.info("Sube un archivo CSV para comenzar el análisis.")
