import pandas as pd
from fastapi import FastAPI
app = FastAPI()

colores_permitidos = ["blanco polar", "verde oliva", "gris oscuro", "terracota", "negro mate"]

def extraer_color(descripcion):
    descripcion_lower = descripcion.lower()
    for color in colores_permitidos:
        if color in descripcion_lower:
            return color
    return "color desconocido"

df = pd.read_csv("pedidos.csv", sep=";")

def cargar_tareas():

    df["color"] = df["descripcion"].apply(extraer_color)
    df["carga"] = pd.to_datetime(df["carga"], dayfirst=True)

    colores_agrupados = df.groupby(["articulo", "color"]).agg({
        "cantidad" : "sum"
    }).reset_index()

    ubicacion_carga = df.groupby(["articulo"]).agg({
        "ubicacion" : "first",
        "carga" : "min"
    }).reset_index()

    agrupado = ubicacion_carga.merge(colores_agrupados, on="articulo")

    resultado = []

    for _, fila in agrupado.iterrows():
        codigo = fila["articulo"]
        color = fila["color"]
        cantidad = fila["cantidad"]
        ubicacion = fila["ubicacion"]
        carga = fila["carga"]

        articulo_encontrado = None

        for item in resultado:
            if item["codigo"] == codigo:
                articulo_encontrado = item
                break

        if articulo_encontrado:
            if color in articulo_encontrado:
                articulo_encontrado["colores"][color] += cantidad
            else:
                articulo_encontrado["colores"][color] = cantidad

        else:
            articulo_nuevo = {
                "codigo" : codigo,
                "ubicacion" : ubicacion,
                "carga" : carga.isoformat(),
                "colores" : {color : cantidad}
            }
            resultado.append(articulo_nuevo)

    sorted_resultado = sorted(resultado, key = lambda x : x["carga"])
    return sorted_resultado

tareas = cargar_tareas()

@app.get("/tareas")
async def listar_tareas():
    return tareas

@app.get("/tareas/0")
async def tarea_prioritaria():
    if not tareas:
        return {"Mensaje" : "No hay tareas disponibles"}
    return tareas[0]

@app.delete("/tareas/0")
async def eliminar_tarea_prioritaria():
    if not tareas:
        return {"mensaje" : "No hay tareas por completar"}
    tarea = tareas.pop(0)
    return {"mensaje" : "Tarea completada", "Tarea" : tarea}
    





