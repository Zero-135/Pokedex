import os, re
from PIL import Image
import os


def resize_images(input_folder, output_folder):
    scale_factor = 0.6667
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith((".png", ".jpg", ".jpeg", ".bmp")):
            filepath = os.path.join(input_folder, filename)
            img = Image.open(filepath)

            new_width = int(img.width * scale_factor)
            new_height = int(img.height * scale_factor)

            # Resize SIN interpolación
            resized = img.resize((new_width, new_height), Image.NEAREST)

            outpath = os.path.join(output_folder, filename)
            resized.save(outpath)


def extraerNombre():
    # Abrir el archivo en modo lectura
    with open(ruta_PBS, "r", encoding="utf-8") as f:
        contenido = f.read()

    # Buscar todas las palabras entre [ ]
    palabras = re.findall(r"\[(.*?)\]", contenido)

    # Mostrar las palabras encontradas
    for palabra in palabras:
        print(palabra)


def renombrar(final_nombre):
    global barra_principal
    # Leer las reglas de renombrado del txt
    reemplazos = {}
    with open(nuevo_txt, 'r', encoding='utf-8') as f:
        for linea in f:
            if '#' in linea:
                if final_nombre:
                    nuevo, viejo = linea.strip().split('#', 1)
                else:
                    viejo, nuevo = linea.strip().split('#', 1)
                reemplazos[viejo.strip()] = nuevo.strip()

    # Renombrar los archivos
    for archivo in os.listdir(carpeta):
        ruta_archivo = os.path.join(carpeta, archivo)
        if os.path.isfile(ruta_archivo):
            nombre_sin_ext, ext = os.path.splitext(archivo)
            barra = barra_principal
            partes = nombre_sin_ext.split("_")
            tam = len(partes)
            nombre_sin_barra = ""

            if tam == 1:
                nombre_sin_barra = partes[0]
            else:
                if tam == 2:
                    nombre_sin_barra = partes[0]
                    barra = "_" + partes[1] + barra
                else:
                    print(nombre_sin_ext)

            # Buscar qué parte del nombre coincide con las claves del diccionario
            for viejo, nuevo in reemplazos.items():
                new_name = viejo.upper().replace(" ", "").replace("'", "").replace("-", "").replace(".", "")
                if new_name == nombre_sin_barra:
                    nuevo_nombre = nombre_sin_barra.replace(new_name, nuevo) + barra + ext
                    # nuevo_nombre = nombre_sin_barra.replace(new_name, nuevo) + ext
                    ruta_nueva = os.path.join(carpeta, nuevo_nombre)
                    os.rename(ruta_archivo, ruta_nueva)
                    # print(f'Renombrado: {archivo} → {nuevo_nombre}')
                    break  # Solo se renombra con la primera coincidencia


# Rutas
carpeta = r'C:\Users\Walter Rivas\Documents\Imagenes\Pokemon\Followers shiny'
ruta_txt = r'D:\PycharmProjects\Pokemon\Pokedex\IndexPokemon.txt'
ruta_PBS = r'C:\Users\Walter Rivas\Documents\Pokemon Base Sky\LA BASE DE SKY\PBS\pokemon.txt'
nuevo_txt = r'D:\PycharmProjects\Pokemon\Pokedex\NamePokemon.txt'
#barra_principal = "_female"
barra_principal = ""
final_nombre_main = True
# True --> De Numero a Nombre
# False --> De Nombre a Numero

# extraerNombre()
renombrar(final_nombre_main)
#resize_images(r"C:\Users\Walter Rivas\Documents\Pokemon Sky 3\Graphics\Pokemon\Back Shiny", r"C:\Users\Walter Rivas\Downloads\Back Shiny")