import pandas as pd
import random
from datetime import datetime, timedelta

# Valores posibles
periodos = ['202210', '202220', '202230', '202310', '202320']
facultades = ['CIENCIAS', 'INGENIERÍA', 'ARTES', 'DERECHO', 'MEDICINA']
departamentos = ['DEP-CIEN', 'DEP-ING', 'DEP-ART', 'DEP-DER', 'DEP-MED']
nombres_departamento = ['Departamento de Ciencias', 'Departamento de Ingeniería', 'Departamento de Artes',
                        'Departamento de Derecho', 'Departamento de Medicina']
estado_curso = ['ACTIVA', 'INACTIVA']
dias = ['LUNES', 'MARTES', 'MIERCOLES', 'JUEVES', 'VIERNES', 'SABADO', 'DOMINGO']

# Función para generar horario aleatorio
def generar_horario():
    hora_inicio = random.choice(range(7, 20)) * 100
    duracion = random.choice([50, 90, 120])
    hora_fin = hora_inicio + ((duracion // 60) * 100 + (duracion % 60))
    return str(hora_inicio).zfill(4), str(hora_fin).zfill(4)

# Generar datos
registros = []
for i in range(100):
    periodo = random.choice(periodos)
    crn = random.randint(10000, 99999)
    cod_materia = f"TEST-{random.randint(1000, 9999)}"
    facultad = random.choice(facultades)
    cod_dep = random.choice(departamentos)
    nom_dep = nombres_departamento[departamentos.index(cod_dep)]
    nombre_curso = f"CURSO DE PRUEBA {i+1}"
    fecha_inicio = datetime(2023, 8, 8)
    fecha_fin = datetime(2023, 12, 8)
    hora_inicio, hora_fin = generar_horario()
    estado = random.choice(estado_curso)

    # Distribución aleatoria de días
    dias_dict = {dia: random.choice([dia[0], '']) for dia in dias}

    registros.append({
        "PERIODO": periodo,
        "CRN": crn,
        "MATERIA": cod_materia,
        "DESCRIPCION_FACULTAD": facultad,
        "CODIGO_DEPARTAMENTO": cod_dep,
        "DESCRIPCION_DEPARTAMENTO": nom_dep,
        "NOMBRE_CURSO": nombre_curso,
        "FECHA_INICIO_FRANJA": fecha_inicio.strftime('%Y-%m-%d'),
        "FECHA_FIN_FRANJA": fecha_fin.strftime('%Y-%m-%d'),
        "HORA_INICIO_FRANJA": hora_inicio,
        "HORA_FIN_FRANJA": hora_fin,
        "DESCRIPCION_ESTADO_DEL_CURSO": estado,
        **dias_dict
    })

# Convertir a DataFrame
df = pd.DataFrame(registros)

# Guardar como CSV
df.to_csv("./data/dataset_cursos_prueba.csv", index=False)
print("✅ Dataset de prueba generado: ./data/dataset_cursos_prueba.csv")
