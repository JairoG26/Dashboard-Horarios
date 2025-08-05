from extraction import cargar_datos_csv
from transformation import generar_modelo
from loading import cargar_tabla
from config import (
    TABLA_DIM_CURSO,
    TABLA_DIM_FRANJA,
    TABLA_DIM_DIA,
    TABLA_DIM_PERIODO,
    TABLA_DIM_GRUPO,
    TABLA_HECHOS_FRANJA,
    TABLA_HECHOS_HORARIO,
)

# 1. Extraer
df = cargar_datos_csv("./data/dataset_cursos_prueba.csv")

# 2. Transformar
datos = generar_modelo(df)
dim_curso = datos["dim_curso"]
dim_franja = datos["dim_franja"]
dim_dia = datos["dim_dia"]
dim_grupo = datos["dim_grupo"]
dim_periodo = datos["dim_periodo"]
hechos_franja = datos["hechos_franja"]
hechos_horario = datos["hechos_horario"]

# 3. Cargar

cargar_tabla(dim_curso, TABLA_DIM_CURSO)
cargar_tabla(dim_franja, TABLA_DIM_FRANJA)
cargar_tabla(dim_dia, TABLA_DIM_DIA)
cargar_tabla(dim_grupo, TABLA_DIM_GRUPO)
cargar_tabla(dim_periodo, TABLA_DIM_PERIODO)
cargar_tabla(hechos_franja, TABLA_HECHOS_FRANJA)
cargar_tabla(hechos_horario, TABLA_HECHOS_HORARIO)