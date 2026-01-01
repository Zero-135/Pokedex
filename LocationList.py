import requests
import pyodbc
from bs4 import BeautifulSoup
import re


def listaPokemonUbicacion(lin):
    url = base + '/wiki/' + lin
    page = urllink(url)
    # Supongamos que ya tienes el HTML cargado en 'page.content'
    soup = BeautifulSoup(page.content, 'html.parser')

    # 1️⃣ Encuentra los spans delimitadores
    inicio = soup.find('span', id='Pok.C3.A9mon')
    fin = soup.find('span', id='Trainers')
    if inicio is None:
        return
    if fin is None:
        fin = inicio.find_next('h2')

    # 2️⃣ Buscar todas las tablas roundy "padre" entre los spans
    tablas = []
    zone = []
    if inicio and fin:
        for elem in inicio.find_all_next():
            if elem == fin:
                break
            if elem.name == 'table' and 'roundy' in elem.get('class', []):
                # Solo agregar si no está dentro de otra tabla roundy
                if not elem.find_parent('table', class_='roundy'):
                    anterior = elem.find_previous_sibling()
                    # Verificar si existe y si es un <h4>
                    texto_h4 = ""
                    if anterior and anterior.name == "h4":
                        texto_h4 = anterior.get_text(separator="\n", strip=True)
                    tablas.append(elem)
                    zone.append(texto_h4)

    for a, valor in enumerate(tablas):
        tabla = valor

        # ✅ Obtener solo los <tr> que no están dentro de otra tabla
        filas_padre = [
            tr for tr in tabla.find_all('tr')
            if tr.find_parent('table') == tabla
        ]
        condition = ''
        for b, tr in enumerate(filas_padre[1:-1]):
            celds = [td.get_text(separator="\n", strip=True) for td in tr.find_all('td')]
            game = ""
            gen = ""
            if not celds:
                condition = tr.find_all('th')[0].get_text(separator="\n", strip=True)
                continue
            trList = tr.find_all('th')
            for th in trList[1:]:
                aTag = th.find_all('a')
                if len(aTag) == 0:
                    continue
                game = aTag[0].get_text(separator="\n", strip=True)
                gen = aTag[0]["title"]

                name = celds[0].replace("'", "''")
                location = celds[2].replace("'", "''")
                level = celds[5]
                rate_M = celds[6]
                rate_D = celds[6]
                rate_N = celds[6]
                if len(celds) > 7:
                    rate_D = celds[7]
                if len(celds) > 8:
                    rate_N = celds[8]
                routes = soup.find('span', class_='mw-page-title-main').get_text(separator="\n", strip=True)

                InsertDataBase(name, game, location, level, rate_M, rate_D, rate_N,
                               condition.replace("'", "''"),
                               routes.replace("'", "''"),
                               zone[a].replace("'", "''"),
                               gen.replace("'", "''"))


def listaPokemonUbicacionGameCorner(lin):
    url = base + '/wiki/' + lin
    page = urllink(url)
    # Supongamos que ya tienes el HTML cargado en 'page.content'
    soup = BeautifulSoup(page.content, 'html.parser')

    # 1️⃣ Encontrar el <span> con el id dado
    gen_Corner = ['Generation_I_3', 'Generation_II_2', 'Generation_III_3', 'Generation_IV_2', 'Generation_IV']

    for gen in gen_Corner:
        span = soup.find('span', id=gen)

        if span is None:
            continue
        # 2️⃣ Obtener la primera tabla después del span
        main_table = span.find_next('table')

        main_body = main_table.find('tbody')

        # Obtener todas las filas <tr>
        trs = main_body.find_all('tr', recursive=False)[1:]

        for j, tr in enumerate(trs, 1):
            tds_hijos = tr.find_all('td', recursive=False)
            for k, td in enumerate(tds_hijos, 1):
                tables_new = td.find_all('table', recursive=False)
                for l, tn in enumerate(tables_new, 1):
                    main_body2 = tn.find('tbody')
                    tr1 = (main_body2.find_all('tr', recursive=False))[0]
                    nameAG = tr1.get_text().split("/")[0].strip()
                    if ('Pokémon' not in nameAG and
                            'Pocket Monsters' not in nameAG):
                        continue
                    nameAG = nameAG.replace("Pokémon ", "")
                    arrName = []
                    if nameAG == 'Pokémon':
                        # arrName = ["HeartGold", "SoulSilver"]
                        FatTable = (tr1.find_parent().find_parent().find_parent()
                                    .find_parent().find_parent().find_parent())
                        h4 = FatTable.find_previous("h4")
                        arrName = [h4.get_text().strip()]
                    else:
                        arrName = nameAG.split(" and ")
                        # No Cuenta Siglas Juego
                        arrName = [tr1.get_text().strip()]

                    for ng in arrName:
                        nameGame = getName(ng)
                        # No Cuenta Siglas Juego
                        nameGame = ng

                        alltr = main_body2.find_all('tr', recursive=False)[1:]
                        for m, atr in enumerate(alltr, 1):
                            alltd = atr.find_all('td', recursive=False)

                            for n, atd in enumerate(alltd, 1):
                                if len(atd.find_all('tr')) == 0:
                                    continue
                                tr1 = atd.find_all('tr')[0]
                                tr2 = atd.find_all('tr')[1]

                                # obtener todas las celdas <td> de esa fila
                                tds = tr1.find_all('td')[1]
                                a_tag = tds.find('a')
                                after_html = ''.join(str(sib) for sib in a_tag.next_siblings)
                                after_soup = BeautifulSoup(after_html, 'html.parser')
                                text = after_soup.get_text(strip=True)
                                match = re.search(r'\d+', text)
                                name = a_tag.get_text(strip=True)
                                level = match.group()
                                condition = tr2.get_text().strip()
                                location = 'Prize'
                                rate = '-'
                                routes = soup.find('span', class_='mw-page-title-main').get_text(separator="\n",
                                                                                                 strip=True)
                                zone = ''

                                InsertDataBase(name, nameGame, location, level, rate, rate, rate,
                                               condition.replace("'", "''"),
                                               routes.replace("'", "''"),
                                               zone.replace("'", "''"),
                                               span.get_text().strip().replace("'", "''"))


def listSpecialEncounters(lin):
    url = base + '/wiki/' + lin
    page = urllink(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    span = soup.find("span", id="Special_encounters")
    if span is None:
        return
    parent = span.find_parent()

    divs = []
    for sib in parent.find_next_siblings():
        if sib.name == "div" and "PKMNcontainer" in sib.get("class", []):
            divs.append(sib)

    for sib in parent.find_next_siblings():
        if sib.name == "div" and "PKMNgrid" in sib.get("class", []):
            new_div = sib.find_all("div", class_="PKMNcontainer")
            for nd in new_div:
                divs.append(nd)

    for d in divs:
        namePoke = (d.find("div", class_="PKMNnamebox")).find("span").get_text(strip=True)
        level_span = soup.find("span", class_="PKMNlevel")
        for child in level_span.find_all("span"):
            child.extract()

        p = d.find_previous("p")
        div_cap = d.find_all("div", class_="PKMNcaption")
        h3 = d.find_previous("h3")
        level = level_span.get_text(strip=True)
        rate = "-"
        condition = p.get_text(separator="\n", strip=True)
        nameGen = h3.get_text(separator="\n", strip=True).replace("'", "''")
        if len(div_cap) > 0:
            nameGame = div_cap[0].get_text(separator="\n", strip=True)
        else:
            nameGame = nameGen
        location = "SP"
        zone = ""
        routes = (soup.find('span', class_='mw-page-title-main')
                  .get_text(separator="\n", strip=True)).replace("'", "''")
        InsertDataBase(namePoke, nameGame, location, level, rate, rate, rate,
                       condition, routes, zone, nameGen)


def getName(nameG):
    match nameG:
        case 'Red':
            game = 'R'
        case 'Blue':
            game = 'B'
        case 'Pocket Monsters Blue':
            game = 'BJ'
        case 'Yellow':
            game = 'Y'
        case 'Gold':
            game = 'G'
        case 'Silver':
            game = 'S'
        case 'Crystal':
            game = 'C'
        case 'FireRed':
            game = 'FR'
        case 'LeafGreen':
            game = 'LG'
        case 'HeartGold':
            game = 'HG'
        case 'SoulSilver':
            game = 'SS'
        case _:
            game = 'HG'

    return game


def urllink(url):
    try:
        return requests.get(url)
    except:
        return urllink(url)


def InsertDataBase(name, nameGame, location, level, rate1, rate2, rate3, condition, routes, zone, gen):
    query = ("insert into pokelocation values(N'" +
             name + "','" +
             nameGame + "',N'" +
             location + "','" +
             level + "','" +
             rate1 + "','" +
             rate2 + "','" +
             rate3 + "',N'" +
             condition + "',N'" +
             routes + "',N'" +
             zone + "',N'" +
             gen + "')"
             )
    cursor.execute(query)
    conn.commit()


base = 'https://bulbapedia.bulbagarden.net'
route = 'Kanto_Route_12'
game_Corner = ['Celadon_Game_Corner', 'Goldenrod_Game_Corner']
server = '(LocalDb)\\MSSQLLocalDB'
bd = 'LocationPokemon'
numberId = 1
modo_gamecorner = False
try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + bd +
                          ';Integrated Security=True')
    cursor = conn.cursor()
    cursor.execute("truncate table pokelocation")
    conn.commit()
except:
    print("Error")

if modo_gamecorner:
    listaPokemonUbicacion(route)
    # for gamC in game_Corner:
    #    listaPokemonUbicacionGameCorner(gamC)
    listSpecialEncounters(route)
else:
    with open("..\Txts\RoutesPokemon.txt", "r", encoding="utf-8") as f:
        for linea in f:
            listaPokemonUbicacion(linea.strip())
            listaPokemonUbicacionGameCorner(linea.strip())
            listSpecialEncounters(linea.strip())
