import random
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# -----------------------------
# Parámetros de simulación
# -----------------------------
n_dias = 180  # 6 meses de datos
plantas = ["Planta A", "Planta B", "Planta C"]
turnos = ["Mañana", "Tarde", "Noche"]

# Lista donde guardamos los registros
data = []

# Fecha de inicio
fecha_inicio = datetime(2023, 1, 1)

# -----------------------------
# Generar datos simulados
# -----------------------------
for dia in range(n_dias):
    fecha = fecha_inicio + timedelta(days=dia)

    for planta in plantas:
        for turno in turnos:
            
            # Producción base distinta por planta y turno
            base_prod = {
                "Planta A": random.randint(800, 1000),
                "Planta B": random.randint(700, 900),
                "Planta C": random.randint(600, 850)
            }[planta]

            # Penalización si es turno de noche
            if turno == "Noche":
                base_prod = int(base_prod * random.uniform(0.85, 0.95))

            # Variación diaria
            produccion = int(base_prod + np.random.normal(0, 50))

            # Defectos proporcionales a producción, pero con ruido
            defectos = max(0, int(produccion * random.uniform(0.02, 0.07)))

            # Paros en minutos (más probables en Planta C)
            if random.random() < 0.1:
                paros = random.randint(20, 120)
            else:
                paros = random.randint(0, 15) if planta != "Planta C" else random.randint(5, 50)

            # Disponibilidad calculada (ejemplo simple)
            disponibilidad = max(0, 100 - paros * 0.5)

            # Guardamos registro
            data.append({
                "Fecha": fecha,
                "Planta": planta,
                "Turno": turno,
                "Produccion": produccion,
                "Defectos": defectos,
                "Paros_min": paros,
                "Disponibilidad_%": disponibilidad
            })

# -----------------------------
# Convertir a DataFrame
# -----------------------------
df = pd.DataFrame(data)

# Introducir valores faltantes aleatorios (ejemplo realista)
for col in ["Produccion", "Defectos", "Paros_min"]:
    idx = np.random.choice(df.index, size=int(0.02*len(df)), replace=False)
    df.loc[idx, col] = np.nan

print(df.head(10))

# Guardar dataset
df.to_csv("datos_produccion.csv", index=False)
