import os
import shutil

# Lista de carpetas de origen
carpetas_origen = [
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Front",
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Front Shiny",
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Back",
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Back Shiny",
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Icons",
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Icons Shiny",
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Followers",
    r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Followers Shiny"
]

# Carpeta de destino
carpeta_destino = r"C:\Users\Walter Rivas\Downloads\Pokes\Pokemon\Union"

# Crear carpeta destino si no existe
os.makedirs(carpeta_destino, exist_ok=True)

contador_carpeta = 0
tamanio = len(carpetas_origen)
for carpeta in carpetas_origen:
    contador = 0
    for ruta_actual, carpetas, archivos in os.walk(carpeta):
        for archivo in archivos:
            extension = os.path.splitext(archivo)[1]  # conserva la extensión
            nuevo_nombre = f"{(contador*tamanio + contador_carpeta%tamanio):05d}{extension}"  # correlativo con ceros
            ruta_origen = os.path.join(ruta_actual, archivo)
            ruta_destino = os.path.join(carpeta_destino, nuevo_nombre)
            shutil.copy2(ruta_origen, ruta_destino)
            print(f"Copiado: {archivo} → {nuevo_nombre}")
            contador += 1
    contador_carpeta = contador_carpeta + 1

print("✅ Copia finalizada.")
