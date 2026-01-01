import requests
import pyodbc
from bs4 import BeautifulSoup
import re


def listaPokemonUbicacion(lin, regionText):
    if lin in game_Corner:
        listaPokemonUbicacionGameCorner(lin, regionText)
        return
    if lin in safari_zone:
        listaPokemonUbicacionSafari(lin, regionText)
        return

    url = base + lin
    page = urllink(url)
    # Supongamos que ya tienes el HTML cargado en 'page.content'
    soup = BeautifulSoup(page.content, 'html.parser')

    # 1️⃣ Encuentra los spans delimitadores
    inicio = soup.find('span', id='Pok.C3.A9mon')
    if inicio is None:
        return
    fin = (soup.find('span', id='Trainers') or
           soup.find('span', id='Layout') or
           inicio.find_next('h2'))
    if fin is None:
        return

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

    for a, tabla in enumerate(tablas):
        anterior = tabla.find_previous("h5")
        if anterior is not None:
            anteriorText = anterior.get_text().strip()
            if anteriorText == "Legends: Arceus":
                print(lin)
                continue

        # ✅ Obtener solo los <tr> que no están dentro de otra tabla
        filas_padre = [
            tr for tr in tabla.find_all('tr')
            if tr.find_parent('table') == tabla
        ]
        filas_padre = filas_padre[1:]

        condition = ''
        for b, tr in enumerate(filas_padre):
            # celds = [td.get_text(separator="\n", strip=True) for td in tr.find_all('td', recursive=False)]

            hijos = tr.find_all(recursive=False)
            if len(hijos) == 1:
                condition = hijos[0].get_text(separator="\n", strip=True)
                continue
            if len(hijos) < 6:
                continue
            celds = []
            games = []
            count = 0
            form = ""
            for c, h in enumerate(hijos):
                if c == 0:
                    # Unown
                    img = h.find("img")
                    if img is not None:
                        text = img["src"]
                        textUnown = (((text.split("/"))[-1]).split("."))[0]
                        form = textUnown.replace("201", "").replace("MS3", "")
                        form = form.replace("48px-", "").replace("MSBDSP", "")
                        form = form.replace("QU", "?").replace("EX", "!")
                        if form == '':
                            form = "A"
                    #

                    celds.append(h.get_text(separator="\n", strip=True))
                if c > 0:
                    if count < 6:
                        count = count + int(hijos[c].get('colspan', 1))
                        games.append(h)
                    else:
                        celds.append(h.get_text(separator="\n", strip=True))
            for th in games:
                aTag = th.find_all('a')
                if len(aTag) == 0:
                    continue
                game = aTag[0].get_text(separator="\n", strip=True)

                if len(celds) < 4:
                    continue

                name = celds[0].replace("'", "''")
                if name == '':
                    continue
                if name == 'Unown':
                    name = name + " " + form
                location = celds[1].replace("'", "''")
                level = celds[2]
                rate_M = celds[3]
                rate_D = celds[3]
                rate_N = celds[3]
                if len(celds) > 4:
                    rate_D = celds[4]
                if len(celds) > 5:
                    rate_N = celds[5]
                routes = soup.find('span', class_='mw-page-title-main').get_text(separator="\n", strip=True)

                InsertDataBase(name, game, location, level, rate_M, rate_D, rate_N,
                               condition.replace("'", "''"),
                               routes.replace("'", "''"),
                               zone[a].replace("'", "''"),
                               getGen(game, regionText))


def listaPokemonUbicacionHisui(lin, regionText):
    global gamesArceus
    url = base + lin
    page = urllink(url)
    # Supongamos que ya tienes el HTML cargado en 'page.content'
    soup = BeautifulSoup(page.content, 'html.parser')

    # 1️⃣ Encuentra los spans delimitadores
    inicio = soup.find('span', id='Pok.C3.A9mon')
    if inicio is None:
        return
    fin = (soup.find('span', id='Trainers') or
           soup.find('span', id='Layout') or
           inicio.find_next('h2'))
    if fin is None:
        return

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

    for a, tabla in enumerate(tablas):
        anterior = tabla.find_previous(["h2", "h3", "h4", "h5"])
        anteriorText = anterior.get_text().strip()
        if anteriorText != "Legends: Arceus" and anteriorText != "Pokémon":
            continue

        # ✅ Obtener solo los <tr> que no están dentro de otra tabla
        filas_padre = [
            tr for tr in tabla.find_all('tr')
            if tr.find_parent('table') == tabla
        ]
        filas_padre = filas_padre[1:]

        condition = ''
        titleLits = []

        next_tag = tabla.find_next_sibling()
        notas = {}
        listLi = []
        if next_tag and next_tag.name == "div" and "mw-references-wrap" in next_tag.get("class", []):
            listLi = next_tag.select("ol.references > li")

        for li in listLi:
            # obtiene "cite_note-2-3" → extraemos el número principal
            match = re.search(r"-(\d+)$", li["id"])
            if match:
                num = match.group(1)
                notas[f"note {num}"] = li.get_text().strip()

        for b, tr in enumerate(filas_padre):
            if b == 0:
                ths = tr.find_all(recursive=False)
                for th in ths:
                    aTag = th.find_all("a")
                    titleLits.append(aTag[0]["title"])
                continue

            hijos = tr.find_all(recursive=False)
            if len(hijos) == 1:
                condition = hijos[0].get_text(separator="\n", strip=True)
                continue
            if len(hijos) < 5:
                continue
            celds = []
            form = ""
            texto_nota = ""
            for c, h in enumerate(hijos):
                if c == 0:
                    # Unown
                    img = h.find("img")
                    if img is not None:
                        text = img["src"]
                        textUnown = (((text.split("/"))[-1]).split("."))[0]
                        form = textUnown.replace("201", "").replace("MS3", "")
                        form = form.replace("48px-", "").replace("MSBDSP", "")
                        form = form.replace("56px-Menu_LA_", "")
                        form = form.replace("QU", "?").replace("EX", "!")
                        if form == '':
                            form = "A"
                    #
                    sup = h.find("sup", class_="reference")
                    if sup:
                        nota_num = sup.get_text(strip=True).replace("[","").replace("]","")
                    else:
                        nota_num = None

                    texto_nota = notas.get(nota_num, "")

                    namePoke = h.get_text().strip()
                    celds.append(re.sub(r"\s*\[[^\]]*\]", "", namePoke).strip())

                countColspan = int(hijos[c].get('colspan', 1))
                for _ in range(countColspan):
                    if c > 0:
                        celds.append(h.get_text(separator="-").strip())
            for game in gamesArceus:
                if len(celds) < 4:
                    continue

                name = celds[0].replace("'", "''")
                if name == '':
                    continue
                if 'Unown' in name:
                    name = name + " " + form
                level = celds[1]
                alpha_level = celds[2]
                routes = soup.find('span', class_='mw-page-title-main').get_text().strip()
                celds = celds[3:]

                InsertDataBaseArceus(name, game, level, alpha_level, titleLits, celds,
                                     condition.replace("'", "''"),
                                     routes.replace("'", "''"),
                                     texto_nota.replace("'", "''"),
                                     getGen(game, regionText))


def listaPokemonUbicacionSafari(lin, regionText):
    global gamesSafari
    if lin != '/wiki/Johto_Safari_Zone':
        return
    url = base + lin
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

    for a, tabla in enumerate(tablas[1:], start=1):
        # ✅ Obtener solo los <tr> que no están dentro de otra tabla
        if a % 2 == 1:
            continue

        inicio = tabla.find_previous("h4")
        fin = tabla.find_previous("table")

        contenido_entre = []
        for elem in inicio.next_siblings:
            if elem == fin:
                break
            if getattr(elem, "name", None) == "p":
                contenido_entre.append(elem)

        zone = inicio.get_text().strip()
        description = " ".join(e.get_text().strip() for e in contenido_entre if hasattr(e, "get_text"))
        description = (description.replace("'", "''")).strip()

        filas_padre = [
            tr for tr in tabla.find_all('tr')
            if tr.find_parent('table') == tabla
        ]
        filas_padre = filas_padre[1:]

        games = gamesSafari
        result = []
        pending = {}  # guarda las celdas con rowspan

        # Primera pasada: calcular número total de columnas
        max_cols = 0
        for tr in filas_padre:
            count = 0
            for td in tr.find_all('td'):
                colspan = int(td.get('colspan', 1))
                count += colspan
            max_cols = max(max_cols, count)

        # Segunda pasada: procesar las filas
        for row_idx, tr in enumerate(filas_padre):
            cells = []
            col_idx = 0

            # Insertar los valores pendientes (por rowspan)
            while col_idx in pending:
                cells.append(pending[col_idx]['value'])
                pending[col_idx]['rowspan'] -= 1
                if pending[col_idx]['rowspan'] == 0:
                    del pending[col_idx]
                col_idx += 1

            for td in tr.find_all('td'):
                value = td.get_text(strip=True)
                rowspan = int(td.get('rowspan', 1))
                colspan = int(td.get('colspan', 1))

                for _ in range(colspan):
                    cells.append(value)
                    if rowspan > 1:
                        pending[col_idx] = {'value': value, 'rowspan': rowspan - 1}
                    col_idx += 1

                # Si hay celdas pendientes que coinciden con las siguientes columnas
                while col_idx in pending:
                    cells.append(pending[col_idx]['value'])
                    pending[col_idx]['rowspan'] -= 1
                    if pending[col_idx]['rowspan'] == 0:
                        del pending[col_idx]
                    col_idx += 1

            # Si faltan columnas, completar con pendientes
            while len(cells) < max_cols:
                if len(cells) in pending:
                    cells.append(pending[len(cells)]['value'])
                    pending[len(cells) - 1]['rowspan'] -= 1
                    if pending[len(cells) - 1]['rowspan'] == 0:
                        del pending[len(cells) - 1]
                else:
                    cells.append('')  # (en caso extremo, relleno vacío)

            result.append(cells)

        # Mostrar resultados
        for i, fila in enumerate(result, 1):
            for game in games:
                name = fila[1].replace("'", "''")
                location = fila[2].replace("'", "''")
                blockArea1 = fila[3].replace("'", "''")
                blockNumber1 = fila[4].replace("'", "''")
                blockArea2 = fila[5].replace("'", "''")
                blockNumber2 = fila[6].replace("'", "''")
                level = fila[7].replace("'", "''")
                idP = fila[8].replace("'", "''")
                time = fila[9].replace("'", "''")

                InsertDataBaseSafari(name, location, blockArea1, blockNumber1, blockArea2, blockNumber2,
                                     level, idP, time, game, zone, description)


def listaPokemonUbicacionGameCorner(lin, regionText):
    url = base + lin
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
                for lo, tn in enumerate(tables_new, 1):
                    main_body2 = tn.find('tbody')
                    tr1 = (main_body2.find_all('tr', recursive=False))[0]
                    nameAG = tr1.get_text().split("/")[0].strip()
                    if ('Pokémon' not in nameAG
                            and 'Pocket Monsters' not in nameAG):
                        continue
                    nameAG = nameAG.replace("Pokémon ", "")
                    if nameAG == 'Pokémon':
                        FatTable = (tr1.find_parent().find_parent().find_parent()
                                    .find_parent().find_parent().find_parent())
                        h4 = FatTable.find_previous("h4")
                        arrName = [h4.get_text().strip()]
                    else:
                        arrName = nameAG.split("and")

                    for ng in arrName:
                        arrNewName = [x.strip() for x in ng.split(",") if x.strip()]
                        for ann in arrNewName:
                            nameGame = getName(ann.replace("Generation", "").strip(), regionText)
                            for fng in nameGame:
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

                                        InsertDataBase(name, fng, location, level, rate, rate, rate,
                                                       condition.replace("'", "''"),
                                                       routes.replace("'", "''"),
                                                       zone.replace("'", "''"),
                                                       getGen(fng, regionText))
                                    # span.get_text().strip().replace("'", "''"))


def listSpecialEncounters(lin, regionText):
    url = base + lin
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
        level_span = d.find("span", class_="PKMNlevel")
        for child in level_span.find_all("span"):
            child.extract()

        # p = d.find_previous("p")
        div_cap = d.find_all("div", class_="PKMNcaption")
        if d.find_parent("div", class_="PKMNgrid") is not None:
            d = d.find_parent()

        h3 = d.find_previous(["h2", "h3", "h4"])

        inicio = None
        for tag in d.find_previous_siblings():
            if tag.name in ["h2", "h3", "h4", "div"]:
                inicio = tag
                break

        level = level_span.get_text(strip=True)
        rate = "-"
        fin = d
        contenido_entre = []
        for elem in inicio.next_siblings:
            if elem == fin:
                break
            if getattr(elem, "name", None) == "p":
                contenido_entre.append(elem)

        condition = " ".join(e.get_text().strip() for e in contenido_entre if hasattr(e, "get_text"))
        condition = (condition.replace("'", "''")).strip()

        nameGen = h3.get_text().strip().replace("'", "''")
        if len(div_cap) > 0:
            nameGame = div_cap[0].get_text().strip()
            if ("If the player" in nameGame
                    or "Nature" in nameGame
                    or "is in the party" in nameGame
                    or "Chamber" in nameGame
                    or "encounter" in nameGame
                    or "Totem" in nameGame
                    or "Ally" in nameGame
                    or "Stairs" in nameGame
                    or "Cursed" in nameGame):
                condition = nameGame + " " + condition
                nameGame = nameGen
            else:
                # Caso Poni_Grove
                if "Aura:" in nameGame:
                    nameGameArr = nameGame.split("Aura:")
                    condition = nameGame + " " + condition
                    if nameGameArr[0] != '':
                        nameGame = nameGameArr[0]
                    else:
                        nameGame = nameGen
        else:
            nameGame = nameGen

        # arrName = []
        # if nameGame == "Special encounters":
        #    Layout = (soup.find("span", id="Layout")).find_parent()
        #    boxLayout = Layout.find_next("table")
        #    body = boxLayout.find("tbody")
        #    allTrs = body.find_all("tr", recursive=False)
        #    for at in allTrs:
        #        first_inner_tag = at.find()
        #        textF = first_inner_tag.get_text().strip()
        #        textF = textF.replace("Pokémon", "")
        #        arrName.extend(textF.split("and"))
        # else:
        nameGame = nameGame.replace("Pokémon", "")
        arrName = nameGame.split("and")

        for ng in arrName:
            arrNewName = [x.strip() for x in ng.split(",") if x.strip()]
            for ann in arrNewName:
                nameGame = getName(ann.replace("Generation", "").strip(), regionText)
                if len(nameGame) == 0:
                    print(ann.replace("Generation", "").strip())
                    print(lin)
                for fng in nameGame:
                    location = "SP"
                    zone = ""
                    routes = (soup.find('span', class_='mw-page-title-main')
                              .get_text().strip()).replace("'", "''")
                    InsertDataBase(namePoke, fng, location, level, rate, rate, rate,
                                   condition, routes, zone, getGen(fng, regionText))


def listRoamingEncounters(lin, regionText):
    global regF
    url = base + lin
    page = urllink(url)

    soup = BeautifulSoup(page.content, 'html.parser')
    span = soup.find("span", id="List_of_roaming_Pokémon")
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
        namePoke = (d.find("div", class_="PKMNnamebox")).find("span").get_text().strip()
        level_span = d.find("span", class_="PKMNlevel")
        for child in level_span.find_all("span"):
            child.extract()

        div_cap = d.find_all("div", class_="PKMNcaption")
        generation = d.find_previous("h3")

        h4_between = None
        for tag in generation.find_all_next():
            if tag == d:
                break
            if tag.name == 'h4':
                h4_between = tag

        region = h4_between
        level = level_span.get_text().strip()
        rate = "-"
        inicio = region if region else generation

        if d.find_parent("div", class_="PKMNgrid") is not None:
            fin = d.find_parent()
        else:
            fin = d

        contenido_entre = []
        for elem in inicio.next_siblings:
            if elem == fin:
                break
            if getattr(elem, "name", None) == "p":
                contenido_entre.append(elem)

        condition = " ".join(e.get_text().strip() for e in contenido_entre if hasattr(e, "get_text"))
        condition = (condition.replace("'", "''")).strip()

        nameGen = generation.get_text().strip().replace("'", "''")
        if len(div_cap) > 0:
            nameGame = div_cap[0].get_text().strip()
            if "If the player" in nameGame:
                condition = nameGame + " " + condition
                nameGame = nameGen
        else:
            nameGame = nameGen

        nameGame = nameGame.replace("Pokémon", "").replace("Generation", "")
        arrName = nameGame.split("and")

        for ng in arrName:
            arrNewName = [x.strip() for x in ng.split(",") if x.strip()]
            for ann in arrNewName:
                regF = ""
                if region is not None:
                    regF = region.get_text().strip()
                nameGame = getName(ann, regF)
                for fng in nameGame:
                    location = "RO"
                    zone = ""
                    routes = (soup.find('span', class_='mw-page-title-main')
                              .get_text().strip()).replace("'", "''")
                    InsertDataBase(namePoke, fng, location, level, rate, rate, rate,
                                   condition, routes, zone,
                                   generation.get_text().replace("Generation", "").strip())


def getName(nameG, region):
    match nameG:
        case "Red":
            game = ['R']
        case "Blue":
            game = ['B']
        case "Pocket Monsters Blue":
            game = ['BJ']
        case "Yellow":
            game = ['Y']
        case "Gold":
            game = ['G']
        case "Silver":
            game = ['S']
        case "Crystal":
            game = ['C']
        case "Ruby":
            game = ['R']
        case "Sapphire":
            game = ['S']
        case "Emerald":
            game = ['E']
        case "FireRed":
            game = ['FR']
        case "LeafGreen":
            game = ['LG']
        case "Diamond":
            game = ['D']
        case "Pearl":
            game = ['P']
        case "Platinum":
            game = ['Pt']
        case "HeartGold":
            game = ['HG']
        case "SoulSilver":
            game = ['SS']
        case "Black":
            game = ['B']
        case "White":
            game = ['W']
        case "Black 2":
            game = ['B2']
        case "White 2":
            game = ['W2']
        case "X":
            game = ['X']
        case "Y":
            game = ['Y']
        case "Omega Ruby":
            game = ['OR']
        case "Alpha Sapphire":
            game = ['AS']
        case "Sun":
            game = ['S']
        case "Moon":
            game = ['M']
        case "Ultra Sun":
            game = ['US']
        case "Ultra Moon":
            game = ['UM']
        case "Let's Go, Pikachu!":
            game = ['P']
        case "Let's Go, Eevee!":
            game = ['E']
        case "Sword":
            game = ['SW']
        case "Shield":
            game = ['SH']
        case "Brilliant Diamond":
            game = ['BD']
        case "Shining Pearl":
            game = ['SP']
        case "Legends: Arceus":
            game = ['A']
        case "Scarlet":
            game = ['S']
        case "Violet":
            game = ['V']
        case _:
            game = getGame(nameG, region)
    return game


def getGame(gen, region):
    match gen:
        case 'I':
            match region:
                case "Kanto":
                    gameF = ["Red", "Blue", "Yellow"]
                case _:
                    gameF = []
        case 'II':
            match region:
                case "Kanto":
                    gameF = ["Gold", "Silver", "Crystal"]
                case "Johto":
                    gameF = ["Gold", "Silver", "Crystal"]
                case _:
                    gameF = []
        case 'III':
            match region:
                case "Kanto":
                    gameF = ["FireRed", "LeafGreen"]
                case "Sevii_Islands":
                    gameF = ["FireRed", "LeafGreen"]
                case "Hoenn":
                    gameF = ["Ruby", "Sapphire", "Emerald"]
                case _:
                    gameF = []
        case 'IV':
            match region:
                case "Kanto":
                    gameF = ["HeartGold", "SoulSilver"]
                case "Johto":
                    gameF = ["HeartGold", "SoulSilver"]
                case "Sinnoh":
                    gameF = ["Diamond", "Pearl", "Platinum"]
                case _:
                    gameF = []
        case 'V':
            match region:
                case "Unova":
                    gameF = ["Black", "White", "Black 2", "White 2"]
                case _:
                    gameF = []
        case 'VI':
            match region:
                case "Kalos":
                    gameF = ["X", "Y"]
                case "Hoenn":
                    gameF = ["Omega Ruby", "Alpha Sapphire"]
                case _:
                    gameF = []
        case 'VII':
            match region:
                case "Alola":
                    gameF = ["Sun", "Moon", "Ultra Sun", "Ultra Moon"]
                case "Kanto":
                    gameF = ["Let's Go, Pikachu!", "Let's Go, Eevee!"]
                case _:
                    gameF = []
        case 'VIII':
            match region:
                case "Galar":
                    gameF = ["Sword", "Shield"]
                case "Sinnoh":
                    gameF = ["Brilliant Diamond", "Shining Pearl"]
                case "Hisui":
                    gameF = ["Legends: Arceus"]
                case _:
                    gameF = []
        case 'IX':
            match region:
                case "Paldea":
                    gameF = ["Scarlet", "Violet"]
                case "Kitakami":
                    gameF = ["Scarlet", "Violet"]
                case _:
                    gameF = []
        case _:
            gameF = []

    if len(gameF) > 0:
        ngf = []
        for gf in gameF:
            ngf.extend(getName(gf, region))
        gameF = ngf

    return gameF


def urllink(url):
    try:
        return InicioSesion(url)
        # return requests.get(url)
    except:
        return urllink(url)


def InsertDataBase(name, namegame, location, level, rate1, rate2, rate3, condition, routes, zone, gen):
    query = ("insert into pokelocation values(N'" +
             name + "','" +
             namegame + "',N'" +
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


def InsertDataBaseSafari(name, location, blockArea1, blockNumber1, blockArea2, blockNumber2,
                         level, idP, time, game, zone, description):
    query = ("insert into SafariZone values(N'" +
             zone + "',N'" +
             description + "',N'" +
             name + "','" +
             location + "','" +
             blockArea1 + "','" +
             blockNumber1 + "','" +
             blockArea2 + "','" +
             blockNumber2 + "','" +
             level + "','" +
             idP + "','" +
             time + "','" +
             game + "')"
             )
    cursor.execute(query)
    conn.commit()


def InsertDataBaseArceus(name, game, levels, levels_alpha, times_weather, values, condition, route, note, generation):
    cols = ""
    vals = ""
    for i, tw in enumerate(times_weather):
        if cols == "":
            cols = tw.replace(" ", "_")
            vals = "N'" + values[i] + "'"
        else:
            cols = cols + ", " + tw.replace(" ", "_")
            vals = vals + ", " + "N'" + values[i] + "'"

    query = ("insert into POKELOCATION_HISUI(name, game, levels, alpha_levels, " +
             cols + ", condition, note, route, generation) values(N'" +
             name + "','" +
             game + "','" +
             levels + "','" +
             levels_alpha + "'," +
             vals + ",N'" +
             condition + "',N'" +
             note + "',N'" +
             route + "','" +
             generation + "')"
             )
    cursor.execute(query)
    conn.commit()


def InicioSesion(url):
    # Crear sesión (mantiene cookies, autenticación, etc.)
    session = requests.Session()

    # URL de inicio de sesión
    login_url = "https://bulbapedia.bulbagarden.net/w/index.php?title=Special:UserLogin&returnto=Main+Page"

    # Datos del formulario de login
    payload = {
        "username": "Walter135",
        "password": "Mewtwo.135"
    }

    # Enviar el formulario (POST)
    response = session.post(login_url, data=payload)

    # Verificar si inició sesión correctamente
    # if response.ok:
    #    print("✅ Sesión iniciada con éxito")

    return session.get(url)


def getGen(game, region):
    gameF = ""
    match region:
        case 'Kanto':
            match game:
                case "R" | "B" | "Y":
                    gameF = "I"
                case "G" | "S" | "C":
                    gameF = "II"
                case "FR" | "LG":
                    gameF = "III"
                case "HG" | "SS":
                    gameF = "IV"
                case "P" | "E":
                    gameF = "VII"
                case _:
                    gameF = ""
        case 'Johto':
            match game:
                case "G" | "S" | "C":
                    gameF = "II"
                case "HG" | "SS":
                    gameF = "IV"
                case _:
                    gameF = ""
        case 'Hoenn':
            match game:
                case "R" | "S" | "E":
                    gameF = "III"
                case "OR" | "AS":
                    gameF = "VI"
                case _:
                    gameF = ""
        case 'Sevii_Islands':
            match game:
                case "FR" | "LG":
                    gameF = "III"
        case 'Sinnoh':
            match game:
                case "D" | "P" | "Pt":
                    gameF = "IV"
                case "BD" | "SP":
                    gameF = "VIII"
                case _:
                    gameF = ""
        case 'Unova':
            match game:
                case "B" | "W" | "B2" | "W2":
                    gameF = "V"
                case _:
                    gameF = ""
        case 'Kalos':
            match game:
                case "X" | "Y":
                    gameF = "VI"
                case _:
                    gameF = ""
        case 'Alola':
            match game:
                case "S" | "M" | "US" | "UM":
                    gameF = "VII"
                case _:
                    gameF = ""
        case 'Galar':
            match game:
                case "SW" | "SH":
                    gameF = "VIII"
                case _:
                    gameF = ""
        case 'Hisui':
            match game:
                case "A":
                    gameF = "VIII"
                case _:
                    gameF = ""
        case 'Paldea':
            match game:
                case "S" | "V":
                    gameF = "IX"
                case _:
                    gameF = ""
        case 'Kitakami':
            match game:
                case "S" | "V":
                    gameF = "IX"
                case _:
                    gameF = ""
        case _:
            gameF = ""

    return gameF


base = 'https://bulbapedia.bulbagarden.net'
route = '/wiki/Akala_Outskirts|Alola'
game_Corner = ['/wiki/Celadon_Game_Corner', '/wiki/Goldenrod_Game_Corner']
safari_zone = ['/wiki/Johto_Safari_Zone']
gamesSafari = ["HG", "SS"]
gamesArceus = ["A"]
roaming_zone = ['/wiki/Roaming_Pokémon|Null']
server = '(LocalDb)\\MSSQLLocalDB'
bd = 'LocationPokemon'
modo_gamecorner = True

try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + bd +
                          ';Integrated Security=True')
    cursor = conn.cursor()
    cursor.execute("truncate table pokelocation")
    cursor.execute("truncate table SafariZone")
    cursor.execute("truncate table POKELOCATION_HISUI")
    conn.commit()
except:
    print("Error")

if modo_gamecorner:
    arrLin = route.split("|")
    lineaF = arrLin[0].strip()
    regF = arrLin[1].strip()

    listaPokemonUbicacion(lineaF, regF)
    listSpecialEncounters(lineaF, regF)
    # listRoamingEncounters(lineaF, regF)
    # listaPokemonUbicacionHisui(lineaF, regF)
else:
    with open("..\Txts\RoutesPokemon.txt", "r", encoding="utf-8") as f:
        for linea in f:
            arrLin = linea.split("|")
            lineaF = arrLin[0].strip()
            regF = arrLin[1].strip()
            listaPokemonUbicacion(lineaF, regF)
            listSpecialEncounters(lineaF, regF)
            # listaPokemonUbicacionHisui(lineaF, regF)
    for linea in roaming_zone:
        arrLin = linea.split("|")
        lineaF = arrLin[0].strip()
        regF = arrLin[1].strip()
        listRoamingEncounters(lineaF, regF)
