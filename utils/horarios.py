def hhmm_a_minutos(hora):
    hh, mm = int(hora[:2]), int(hora[2:])
    return hh * 60 + mm

def minutos_a_hhmm(minutos):
    hh, mm = divmod(minutos, 60)
    return f"{hh:02d}{mm:02d}"

# Función para redondear horas al periodo de 30 min más cercano
def redondear_hora(hora, tipo="inicio"):
    hh, mm = int(hora[:2]), int(hora[2:])  # Extraer horas y minutos
    if tipo == "inicio":
        mm = 0 if mm < 30 else 30  # Redondear hacia abajo
    else:  # tipo == "fin"
        mm = 30 if mm < 30 else 0  # Redondear hacia arriba
        hh += 1 if mm == 0 else 0  # Si se redondeó a 00, sumamos 1 hora

    return f"{hh:02d}{mm:02d}"  # Devolver en formato HHMM