# grupo_whiskey
# Análisis de Desplazamiento y Precipitación  
**Aplicación Streamlit basada en datos DInSAR**

Este repositorio contiene una aplicación web creada con **Streamlit** para visualizar y analizar series temporales de desplazamiento del terreno y precipitación. El proyecto nace en el marco del **Proyecto Integrador** (Universidad Técnica Particular de Loja) y se apoya en los datos utilizados por *Guamán et al.* (2024) para la urbanización Ciudad Victoria (Loja, Ecuador).

---

## Características principales
- **Carga directa de CSV** mediante `st.file_uploader`.
- **Gráfica dual** desplazamiento ↔ fecha (eje izq.) + precipitación ↔ fecha (eje der.) con anotaciones de lluvia.
- **Cálculo automático** de la fecha con mayor tasa media diaria de desplazamiento.
- **Tabla resumen** con estadísticas descriptivas (media, desviación, mínimos, máximos, etc.).
- Vista previa de los primeros registros del archivo cargado.

---

## Requisitos
| Paquete | Versión mínima |
|---------|----------------|
| Python  | 3.8+           |
| streamlit | 1.20 |
| pandas | 1.5 |
| matplotlib | 3.7 |

> Instala todo con  
> ```bash
> pip install streamlit pandas matplotlib
> ```

---

## Estructura del CSV esperado
| Columna        | Tipo | Descripción                                           |
|----------------|------|-------------------------------------------------------|
| `fecha`        | `dd/mm/aaaa` o `yyyy-mm-dd` | Fecha de registro |
| `54218`, `54219`, … | numérico | Desplazamiento (cm) de cada punto de control |
| `rainfall(mm)` | numérico | Precipitación mensual (mm) |

Cualquier columna que **no** se llame `fecha` ni `rainfall(mm)` se interpreta como desplazamiento.

---

## Cómo ejecutar

1. Clona o descarga el repositorio.  
2. Activa tu entorno y ejecuta:

```bash
streamlit run app.py
