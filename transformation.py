from utils.horarios import hhmm_a_minutos, minutos_a_hhmm, redondear_hora
import pandas as pd

def unir_dias_cursos(df):
    dias = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    columnas_sin_dias = [col for col in df.columns if col not in dias]
    df_unido = df.groupby(columnas_sin_dias, dropna=False)[dias].agg(
        lambda col: col.fillna('').astype(str).apply(lambda x: x.strip()).max()
    ).reset_index()
    return df_unido

def transformar_cursos(df):
    df = unir_dias_cursos(df)
    df = df.dropna(subset=["HORA_INICIO_FRANJA"])
    df["HORA_INICIO"] = df["HORA_INICIO_FRANJA"].astype(float).astype(int).astype(str).str.zfill(4)
    df["HORA_FIN"] = df["HORA_FIN_FRANJA"].astype(float).astype(int).astype(str).str.zfill(4)
    df["HORA_INICIO_REDONDEADA"] = df["HORA_INICIO"].apply(lambda x: redondear_hora(x, "inicio"))
    df["HORA_FIN_REDONDEADA"] = df["HORA_FIN"].apply(lambda x: redondear_hora(x, "fin"))
    df["DURACION_MINUTOS"] = df.apply(lambda row: hhmm_a_minutos(row["HORA_FIN_REDONDEADA"]) - hhmm_a_minutos(row["HORA_INICIO_REDONDEADA"]), axis=1)
    mask = df["MATERIA"] == "ISIS-3007"
    df = pd.concat([df[~mask], df[mask].drop_duplicates(subset=["PERIODO"])], ignore_index=True)
    df["ID"] = range(1, len(df) + 1)
    return df


def generar_franjas(df):
    dias = ["LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    nuevos_registros = []

    for _, row in df.iterrows():
        inicio = hhmm_a_minutos(row["HORA_INICIO_REDONDEADA"])
        fin = hhmm_a_minutos(row["HORA_FIN_REDONDEADA"])
        for t in range(inicio, fin, 30):
            nuevo_row = row.copy()
            nuevo_row["HORA_INICIO_FRANJA"] = minutos_a_hhmm(t)
            nuevo_row["HORA_FIN_FRANJA"] = minutos_a_hhmm(t + 30)
            nuevo_row["FRANJA_HORARIA"] = f"{nuevo_row['HORA_INICIO_FRANJA']}-{nuevo_row['HORA_FIN_FRANJA']}"
            nuevos_registros.append(nuevo_row)

    df_nuevos = pd.DataFrame(nuevos_registros)

    registros_expandidos = []
    for _, fila in df_nuevos.iterrows():
        for dia in dias:
            if pd.notna(fila[dia]) and fila[dia] != "":
                nueva_fila = fila.copy()
                nueva_fila["DIA"] = dia
                registros_expandidos.append(nueva_fila)

    df_expandidos = pd.DataFrame(registros_expandidos)
    # Ya no se eliminan las columnas de los días
    return df_expandidos

def tabla_dias_semana():
    return pd.DataFrame({
        "DIA": ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"],
        "ORDEN": [1, 2, 3, 4, 5, 6, 7]
    })

def generar_dim_curso(df):
    columnas = ["MATERIA", "DESCRIPCION_FACULTAD", "CODIGO_DEPARTAMENTO", "DESCRIPCION_DEPARTAMENTO", "NOMBRE_CURSO", "CRN"]
    df_curso = df[columnas].drop_duplicates().copy()
    df_curso["ID_MATERIA"] = range(1, len(df_curso) + 1)
    return df_curso

def generar_dim_periodo(df):
    df_periodo = df[["PERIODO"]].drop_duplicates().copy()
    df_periodo["ANIO_PERIODO"] = df_periodo["PERIODO"]
    df_periodo["ANIO"] = df_periodo["PERIODO"].astype(str).str[:4]
    return df_periodo

def generar_dim_horario(df_franjas):
    columnas_clave = [
        "FECHA_INICIO_FRANJA", "FECHA_FIN_FRANJA",
        "HORA_INICIO", "HORA_FIN",
        "HORA_INICIO_REDONDEADA", "HORA_FIN_REDONDEADA",
        "LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO", "DURACION_MINUTOS"
    ]
    # Eliminamos duplicados en base a las columnas clave
    df = df_franjas[columnas_clave].drop_duplicates().copy()

    df["ID_HORARIO"] = range(1, len(df) + 1)

    # Normalizamos las horas a string formato HHMM
    df["HORA_INICIO"] = df["HORA_INICIO"].astype(float).astype(int).astype(str).str.zfill(4)
    df["HORA_FIN"] = df["HORA_FIN"].astype(float).astype(int).astype(str).str.zfill(4)

    # Calculamos duración en minutos
    df["DURACION_MINUTOS"] = df.apply(lambda row: hhmm_a_minutos(row["HORA_FIN"]) - hhmm_a_minutos(row["HORA_INICIO"]), axis=1)

    return df

def generar_dim_franja_horaria(df_franjas):
    columnas = ["PERIODO", "DIA", "HORA_INICIO_FRANJA", "HORA_FIN_FRANJA", "FRANJA_HORARIA"]
    df = df_franjas[columnas].drop_duplicates().copy()
    df["ID_FRANJA"] = range(1, len(df) + 1)
    return df

def generar_hechos_horario_curso(df_franjas, dim_horario, dim_curso, dim_periodo):
    # Unimos para obtener el ID_HORARIO
    claves_horario = ["FECHA_INICIO_FRANJA", "FECHA_FIN_FRANJA", "HORA_INICIO", "HORA_FIN",
                      "LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    df = df_franjas.merge(dim_horario, on=claves_horario, how="left")
    # Unimos para obtener el ID_MATERIA
    claves_materia = ["MATERIA", "DESCRIPCION_FACULTAD", "CODIGO_DEPARTAMENTO", "DESCRIPCION_DEPARTAMENTO",
                      "NOMBRE_CURSO", "CRN"]
    df = df.merge(dim_curso, on=claves_materia, how="left")
    # Unimos para obtener el ID_PERIODO
    claves_periodo = ["PERIODO"]
    df = df.merge(dim_periodo, on=claves_periodo, how="left")

    # Creamos la llave primaria compuesta
    df["ID_HORARIO_CURSO"] = df["PERIODO"].astype(str) + "_" + df["ID_MATERIA"].astype(str) + "_" + df["ID_HORARIO"].astype(str)

    hechos = df[["ID_HORARIO_CURSO", "PERIODO", "ID_MATERIA", "ID_HORARIO"]].drop_duplicates().reset_index(drop=True)
    return hechos

def generar_hechos_franjas_curso(df_franjas, dim_franja_horaria, dim_curso, dim_periodo, dim_horario):

    claves_horario = ["FECHA_INICIO_FRANJA", "FECHA_FIN_FRANJA", "HORA_INICIO", "HORA_FIN",
                      "LUNES", "MARTES", "MIERCOLES", "JUEVES", "VIERNES", "SABADO", "DOMINGO"]
    df = df_franjas.merge(dim_horario, on=claves_horario, how="outer")

    claves_franja = ["HORA_INICIO_FRANJA", "HORA_FIN_FRANJA", "PERIODO", "DIA"]
    df = df.merge(dim_franja_horaria, on=claves_franja, how="left")

    claves_materia = ["MATERIA", "DESCRIPCION_FACULTAD", "CODIGO_DEPARTAMENTO", "DESCRIPCION_DEPARTAMENTO",
                      "NOMBRE_CURSO", "CRN"]
    df = df.merge(dim_curso, on=claves_materia, how="left")
    claves_periodo = ["PERIODO"]
    df = df.merge(dim_periodo, on=claves_periodo, how="left")

    df["ID_FRANJA_CURSO"] = df["PERIODO"].astype(str) + "_" + df["ID_MATERIA"].astype(str) + "_" + df["ID_FRANJA"].astype(str) + "_" + df["ID_HORARIO"].astype(str)

    hechos = df[["ID_FRANJA_CURSO", "PERIODO", "ID_MATERIA", "ID_FRANJA", "ID_HORARIO"]].drop_duplicates().reset_index(drop=True)
    return hechos

def generar_modelo(df):

    df_transformados1 = transformar_cursos(df)
    print("Transformación de cursos completada. Número de registros:", len(df_transformados1))
    df_transformados1.head(5)
    df_franjas = generar_franjas(df_transformados1)
    print("Generación de franjas horarias completada. Número de franjas:", len(df_franjas))
    df_horarios = generar_dim_horario(df_transformados1)
    print("Generación de horarios completada. Número de horarios:", len(df_horarios))
    df_cursos = generar_dim_curso(df_transformados1)
    print("Generación de dimensión curso completada. Número de cursos:", len(df_cursos))
    df_periodo = generar_dim_periodo(df_transformados1)
    print("Generación de dimensión periodo completada. Número de periodos:", len(df_periodo))
    df_franjas_horarias = generar_dim_franja_horaria(df_franjas)
    print("Generación de dimensión franja horaria completada. Número de franjas:", len(df_franjas_horarias))
    dim_dia = tabla_dias_semana()
    print("Generación de dimensión día de la semana completada. Número de días:", len(dim_dia))
    hechos_horario = generar_hechos_horario_curso(df_transformados1, df_horarios, df_cursos, df_periodo)
    print("Generación de hechos horario curso completada. Número de hechos:", len(hechos_horario))
    hechos_franja = generar_hechos_franjas_curso(df_franjas, df_franjas_horarias, df_cursos, df_periodo, df_horarios)
    print("Generación de hechos franja curso completada. Número de hechos:", len(hechos_franja))
    

    return {
        "dim_curso": df_cursos,
        "dim_franja": df_franjas_horarias,
        "dim_dia": dim_dia,
        "dim_grupo": df_horarios,
        "dim_periodo": df_periodo,
        "hechos_franja": hechos_franja,
        "hechos_horario": hechos_horario
    }
