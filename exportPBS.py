import pandas as pd
from openpyxl import load_workbook
import os
import sys

# ===============================
# CONFIGURACIÓN
# ===============================
PBS_ROOT = r"C:\Users\Walter Rivas\Documents\PokeProject V4\PBS"
OUTPUT_EXCEL = "pokemon_completo.xlsx"
INDEX_FILE = r"D:\PycharmProjects\Pokemon\Pokedex\NamePokemon.txt"
VALID_PREFIXES = ("pokemon_base", "pokemon_forms")
VALID_NAMES = ("pokemon.txt",)


def load_pokemon_numbers(index_file):
    mapping = {}

    with open(index_file, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or "#" not in line:
                continue

            name, number = line.split("#", 1)
            mapping[name.strip()] = number.strip()

    return mapping


# ===============================
# PARSE PBS
# ===============================
def parse_pbs(file_path, source):
    pokemons = []
    current = {}

    with open(file_path, encoding="utf-8") as f:
        for line in map(str.strip, f):
            if not line:
                continue

            if line.startswith("#-------------------------------"):
                if current:
                    current["Source"] = source
                    pokemons.append(current)
                    current = {}
                continue

            if line.startswith("[") and line.endswith("]"):
                current["InternalName"] = line[1:-1]
                continue

            if "=" in line:
                key, value = line.split("=", 1)
                current[key.strip()] = value.strip()

        if current:
            current["Source"] = source
            pokemons.append(current)

    return pokemons


# ===============================
# BUSCAR ARCHIVOS (NO RECURSIVO)
# ===============================
def find_pokemon_files(root):
    results = []

    for name in os.listdir(root):
        path = os.path.join(root, name)

        if not os.path.isfile(path):
            continue

        if name.startswith(VALID_PREFIXES) or name in VALID_NAMES:
            source = os.path.splitext(name)[0]
            results.append((path, source))

    return results


# ===============================
# EXPORTAR EXCEL
# ===============================
def export_to_excel(data, output, number_map):
    df = pd.DataFrame(data)

    # --------------------------------
    # Separar InternalName e Index
    # --------------------------------
    split = df["InternalName"].str.split(",", n=1, expand=True)
    df["InternalName"] = split[0].str.strip()
    df["Index"] = split[1]

    # --------------------------------
    # Columna Number (desde IndexPokemon)
    # --------------------------------
    df["Number"] = df["InternalName"].map(number_map)

    # --------------------------------
    # COLUMNAS AUXILIARES DE ORDEN
    # --------------------------------
    # Number: vacío primero, luego numérico
    df["NumberSort"] = pd.to_numeric(df["Number"], errors="coerce").fillna(-1)

    # Index: vacío primero, luego 1,2,3...
    df["IndexSort"] = pd.to_numeric(df["Index"], errors="coerce").fillna(-1)

    # --------------------------------
    # ORDEN FINAL
    # --------------------------------
    df = df.sort_values(
        by=["NumberSort", "InternalName", "IndexSort"],
        ascending=[True, True, True]
    )

    # --------------------------------
    # ORDEN DE COLUMNAS (Number = 2ª)
    # --------------------------------
    priority = [
        "Source",
        "Number",
        "InternalName",
        "Index",
        "Name",
        "FormName"
    ]
    cols = priority + [
        c for c in df.columns
        if c not in priority and c not in ("NumberSort", "IndexSort")
    ]
    df = df[cols]

    # --------------------------------
    # EXPORTAR
    # --------------------------------
    df.to_excel(output, index=False)

    wb = load_workbook(output)
    ws = wb.active

    ws.auto_filter.ref = ws.dimensions

    for col in ws.columns:
        max_len = max((len(str(cell.value)) for cell in col if cell.value), default=0)
        ws.column_dimensions[col[0].column_letter].width = max_len + 2

    wb.save(output)
    os.startfile(output)


# ===============================
# MAIN
# ===============================
if __name__ == "__main__":
    pokemon_files = find_pokemon_files(PBS_ROOT)

    if not pokemon_files:
        print("❌ No se encontraron archivos válidos")
        sys.exit(1)

    all_pokemons = []
    for path, source in pokemon_files:
        print(f"✔ Leyendo: {path}")
        all_pokemons.extend(parse_pbs(path, source))

    number_map = load_pokemon_numbers(INDEX_FILE)

    export_to_excel(all_pokemons, OUTPUT_EXCEL, number_map)
    sys.exit()

