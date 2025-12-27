import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import re
from io import StringIO

def procesar_e_insertar(texto):

    # DIVISIÓN EN BLOQUES ---------------------------
        # Cada bloque es una matriz
    bloques = texto.strip().split("\n\n")
        # Ignoramos las matrices que ya estén completas
    if len(bloques) < 2:
        return texto 

    # MATRIZ 1: encabezado + filas -------------------
        # Dividimos la matriz por líneas
    lineas1 = bloques[0].strip().splitlines()
        # Extraemos los encabezados
    encabezado_tarea = lineas1[0]              # [tarea]
    encabezado1 = lineas1[1].split()    # : 1   2   3  ....
        # Para añadir directamente el encabezado, debemos eliminar el caracter ':'
    encabezado1.pop(0)
        # Separamos solamente las lineas binarias (las de datos en sí)
    filas1 = lineas1[2:]

    # MATRIZ 2: encabezado + filas -------------------
    lineas2 = bloques[1].strip().splitlines()
    encabezado2 = lineas2[0].split()
    encabezado2.pop(0)
    filas2 = lineas2[1:]
        # Para calcular en número de columnas extra a añadir calculamos cuantos
        # caracteres (quitando los espacios) hay en una fila y eliminamos el 
        # caracter correspondiente a la columna que indica el número de fila
    fila_no_espacios = ''.join(filas2[0].split())
    num_columnas_extra = len(fila_no_espacios) -1

    # UNIFICACIÓN DE CABECERAS -----------------------
    nueva_cabecera = encabezado1 + encabezado2

    # CONVERTIR PRIMERAS FILAS A DICCIONARIO --------
    datos = {}
    for fila in filas1:
        # Convertimos las filas en conjuntos de números
        partes = fila.split()
        # Tomamos el primer elemento como el id de la fila
        id_fila = partes[0]
        # Tomamos el resto de los elementos como los valores y añadimos 0s 
        # en el resto de filas añadidas
        valores = partes[1:] + ['0'] * len(encabezado2)
        # El diccionario tiene como clave el id y como valor los datos de la fila
        datos[id_fila] = valores
    
    # AÑADIR FILAS DE MATRIZ 2 -----------------------
    for fila in filas2:
        # Procesamos las filas de la segunda matriz del mismo modo
        partes = fila.split()
        fila_id = partes[0]
        valores = partes[1:]
        # En este caso añadimos tantos 0s al inicio como columnas había en la matriz 1
        fila_completa = ['0'] * len(encabezado1) + valores
        datos[fila_id] = fila_completa

    # ORDENAR FILAS NUMÉRICAMENTE --------------------
    filas_ordenadas = sorted(datos.items(), key=lambda x: int(x[0]))

    # CONSTRUIR RESULTADO FINAL ----------------------
    resultado = [encabezado_tarea]
    linea_encabezado = ": "
    for valor in nueva_cabecera:
        if int(valor) < 10:
            linea_encabezado += f"   {valor}"
        elif int(valor) < 100:
            linea_encabezado += f"  {valor}"  # solo 2 espacios si tiene 2 cifras   
        else:
            linea_encabezado += f" {valor}"
    resultado.append(linea_encabezado)

    for fila_id, valores in filas_ordenadas:
        resultado.append(f"{fila_id:<4} " + "   ".join(valores))

    return "\n".join(resultado)


# Función de graficado
def graficar_tareas_por_grupo(lista_tareas, titulo, nombre_archivo):
    horas_usadas = set()
    for task in lista_tareas:
        df = task_data[task]
        for camino, row in df.iterrows():
            for h in df.columns:
                if row[h] == 1:
                    horas_usadas.add(int(h))

    if not horas_usadas:
        return None
    min_hora, max_hora = min(horas_usadas), max(horas_usadas)

    todos_caminos = set()
    for task in lista_tareas:
        todos_caminos.update(task_data[task].index)
    timeline = pd.DataFrame(float('nan'), index=sorted(todos_caminos), columns=range(min_hora, max_hora + 1))

    colormap = plt.colormaps.get_cmap('tab20').resampled(len(lista_tareas))

    for i, task in enumerate(lista_tareas):
        df = task_data[task]
        color_code = i + 1
        for camino, row in df.iterrows():
            for hora in df.columns:
                hora_int = int(hora)
                if hora_int in timeline.columns and row[hora] == 1:
                    timeline.at[camino, hora_int] = color_code


    fig, ax = plt.subplots(figsize=(18, 8))
    cmap = plt.colormaps.get_cmap('tab20').resampled(len(lista_tareas))
    cax = ax.imshow(timeline.values, aspect='auto', cmap=cmap, vmin=1, vmax=len(lista_tareas))
    y_ticks = list(range(0, len(timeline.index), 10))
    y_labels = [i + 1 for i in y_ticks]
    ax.set_yticks(y_ticks)
    ax.set_yticklabels(y_labels)



    for y in range(1, len(timeline.index)):
        ax.axhline(y - 0.5, color='lightgray', linewidth=0.5)

    ax.set_xticks(range(len(timeline.columns)))
    ax.set_xticklabels(timeline.columns, rotation=90)

    ax.set_xlabel('Hours')
    ax.set_ylabel('Rows')
    ax.set_title(titulo)
    handles = [mpatches.Patch(color=cmap(i), label=task) for i, task in enumerate(lista_tareas)]
    ax.legend(handles=handles, bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.tight_layout()
    fig.savefig(f"{nombre_archivo}.png")
    plt.close()
    print(f"Gráfico guardado en: {nombre_archivo}.png")




# 1. Leer archivo crudo con todos los bloques
with open("tierra2.txt", "r", encoding="utf-8") as file:
    texto = file.read()

# 2. Limpiamos el archivo para evitar errores en la lectura del documento
texto = re.sub(r'^x\d+\[i,k,l\]', '', texto, flags=re.MULTILINE)
texto = re.sub(r':=', '', texto)
texto = re.sub(r',\*,\*', '', texto)
texto = re.sub(r';', '', texto)

# 3. Dividir por bloques de tareas tipo "[tarea]"
bloques_raw = re.split(r'\n(?=\s*\[[a-zA-Z0-9]+\])', texto)

# 4. Aplicar procesar_e_insertar a cada bloque y guardar resultado por tarea
task_data = {}
for bloque in bloques_raw:
    bloque = bloque.strip()
    if not bloque:
        continue
    tabla_limpia = procesar_e_insertar(bloque)
    print("Tabla procesada:\n", tabla_limpia)
    
    # Extraer el nombre de la tarea del bloque original
    nombre_match = re.search(r'\[\s*([a-zA-Z0-9_]+)\s*\]', bloque)

    print("Nombre de tarea extraído:", nombre_match)
    if nombre_match:
        nombre_tarea = nombre_match.group(1)
        # Convertir a DataFrame
        tabla_io = StringIO(tabla_limpia.split('\n', 1)[1])  # omitir línea [nombre]
        df = pd.read_csv(tabla_io, delim_whitespace=True)
        df = df.set_index(df.columns[0])
        df.index = df.index.astype(int)
        df.columns = df.columns.astype(int)
        task_data[nombre_tarea] = df
print("Tareas encontradas:", list(task_data.keys()))


# 5. Definir tareas pre y post plantado
tareas_pre_plantado1 = ["preparartierra1", "papel1", "plantar1", "ponerarquillo1", "ponermalla1", "ponerriego1"]
tareas_post_plantado1 = ["quitarmalla1","quitararquillo1", "quitarriego1", "cosechar1"]
tareas_pre_plantado2 = ["preparartierra2", "sembrar2", "ponerriego2"]
tareas_post_plantado2 = ["quitarriego2", "cosechar2"]

# 6. Generar gráficos
#graficar_tareas_por_grupo(tareas_pre_plantado1, "Pre-planting tasks", "grafico_pre_siembra1")
#graficar_tareas_por_grupo(tareas_post_plantado1, "Post-planting tasks", "grafico_post_siembra1")
graficar_tareas_por_grupo(tareas_pre_plantado2, "Pre-planting tasks", "grafico_pre_siembra2")
graficar_tareas_por_grupo(tareas_post_plantado2, "Post-planting tasks", "grafico_post_siembra2")



