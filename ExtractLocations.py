from bs4 import BeautifulSoup
import requests


def listaRoutes(reg):
    url = base + '/wiki/' + reg
    page = urllink(url)

    soup = BeautifulSoup(page.content, "html.parser")

    lastDiv = soup.find_all("table", class_="roundy")[-1]

    # 1️⃣ Eliminar todas las etiquetas <b> (y su contenido)
    for b_tag in lastDiv.find_all("b"):
        b_tag.decompose()  # elimina completamente el tag <b> del árbol

    # 2️⃣ Extraer todos los href de las etiquetas <a>
    hrefs = [a["href"] for a in lastDiv.find_all("a", href=True)]

    # 3️⃣ Mostrar resultados
    for link in hrefs:
        # print(link.replace("/wiki/",""))
        link = link.split("#")[0]
        if not any(d["link"] == link and d["reg"] == reg for d in listRoutesTxt):
            listRoutesTxt.append({"reg": reg, "link": link})
            dlTag(reg, link)


def dlTag(reg, lin):
    url = base + lin
    page = urllink(url)

    soup = BeautifulSoup(page.content, "html.parser")

    # 1️⃣ Buscar el <span> con id="Places_of_interest"
    span_tag = soup.find("span", id="Places_of_interest")

    # 2️⃣ Buscar todos los <dl> que aparecen después del span
    dl_tags = span_tag.find_all_next("dl") if span_tag else []

    # 3️⃣ Obtener los href de cada <a> dentro de cada <dl>
    resultado = []

    for i, dl in enumerate(dl_tags, start=1):
        enlaces = [a["href"] for a in dl.find_all("a", href=True)]
        resultado.append({
            "dl_index": i,
            "hrefs": enlaces
        })

    # 4️⃣ Mostrar los resultados
    for dl_data in resultado:
        for link in dl_data["hrefs"]:
            link = link.split("#")[0]
            if not any(d["link"] == link and d["reg"] == reg for d in listRoutesTxt):
                listRoutesTxt.append({"reg": reg, "link": link})


def urllink(url):
    try:
        return requests.get(url)
    except:
        return urllink(url)


base = 'https://bulbapedia.bulbagarden.net'
region = ['Alola']
# region = ['Kanto', 'Johto', 'Hoenn', 'Sevii_Islands', 'Sinnoh', 'Unova', 'Kalos', 'Alola',
#          'Galar', 'Isle_of_Armor', 'Crown_Tundra', 'Hisui', 'Paldea', 'Kitakami']

# region = ['Kanto', 'Johto', 'Hoenn', 'Sevii_Islands', 'Sinnoh', 'Unova',
#          'Kalos', 'Alola', 'Galar', 'Hisui', 'Paldea', 'Kitakami']

listRoutesTxt = list()

for reg in region:
    listaRoutes(reg)
listRoutesTxt = sorted(listRoutesTxt, key=lambda x: x["link"])
with open("..\Txts\RoutesPokemon.txt", "w", encoding="utf-8") as f:
    for link in listRoutesTxt:
        f.write(link["link"]+ "|" + link["reg"] + "\n")
