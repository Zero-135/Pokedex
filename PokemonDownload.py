import os
import re
import requests
from bs4 import BeautifulSoup


def listaPokemon():
    url = base + '/wiki/Lista_de_Pokémon'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.find_all("table", class_=re.compile("^tabpokemon"))
    numberPokemon = ''
    for table in tables:
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            numbertds = len(tds)
            if numbertds == 0 or numbertds == 1 or numbertds == 2:
                continue

            if numbertds == 4:
                number = 0
                name = 1
                numberPokemon = formatText(tds[0].text)
            else:
                name = 0

            urlPokemon = base + (tds[name].find_all('a'))[0]['href']
            namePokemon = formatText(tds[name].text)

            nameFile = "../Pokemon/Pokedex Nacional/" + numberPokemon + "-" + namePokemon + ".png"
            if not os.path.exists(nameFile):
                loadPage(nameFile, urlPokemon)


def loadPage(nameFile, urlPokemon):
    page = urllink(urlPokemon)
    soup = BeautifulSoup(page.content, 'html.parser')

    try:
        image = soup.find_all("div", class_=re.compile("^imageswitch_scale"))[0]
        urlPokemonDownload = base + (image.find_all('a'))[0]['href']

        page = urllink(urlPokemonDownload)
        soup = BeautifulSoup(page.content, 'html.parser')
        image = soup.find_all("div", class_=re.compile("^fullImageLink"))[0]
        urlPokemonDownload = image.find_all('a')[0]['href']

        downloadImage(nameFile, urlPokemonDownload)
    except NameError:
        print(NameError)


def loadPage2(namePokemon, urlPokemon):
    global number
    page = urllink(urlPokemon)
    soup = BeautifulSoup(page.content, 'html.parser')
    classFind = "radius10"
    megaGiga = False
    tagDifferent = 1
    countTag = 1

    if len(namePokemon.split("-")) > 1:
        classFind = "evolucion"
        megaGiga = True
        tagDifferent = 0

    try:
        images = soup.find_all("table", class_=re.compile("^" + classFind))
        tamMegaGiga = len(images)
        for image in images:
            if (not megaGiga and countTag > 1) or (megaGiga and countTag == tamMegaGiga):
                continue

            finddiv = ""
            allTr = image.find_all("tr")
            length = len(allTr) - tagDifferent
            sum = 0

            if length < 5:
                finddiv = "td"
                sum = length

            if length % 6 == 0:
                finddiv = "td"
                sum = 6

            if length % 5 == 0:
                finddiv = "td"
                sum = 5

            if namePokemon == "Arceus":
                finddiv = "th"
                sum = 4

            if namePokemon == "Necrozma":
                finddiv = "td"
                sum = 4

            if sum == 0:
                sum = 0

            count = 0
            while count < length:  # Filas: Ejemplo con los arceus
                tdLinks = allTr[count].find_all('td', class_=None)
                trNames = []

                if namePokemon == "Necrozma" or megaGiga:
                    tdLinks = image.find_all('td', class_=None)
                else:
                    trNames = allTr[count + 1].find_all(finddiv)

                for x in range(0, len(tdLinks)):
                    urlPokemonDownload = base + tdLinks[x].find_all('a')[0]['href']

                    if urlPokemonDownload in listUrlPokemonImage:
                        continue

                    listUrlPokemonImage.append(urlPokemonDownload)

                    if namePokemon == "Necrozma" and x == 4:
                        continue

                    if namePokemon == "Necrozma" or megaGiga:
                        if urlPokemonDownload == base + "/wiki/Archivo:Necrozma_HOME.png":
                            nameFile = formatText(tdLinks[x].find_all('a')[1].text)
                        else:
                            nameFile = formatText(tdLinks[x].find_all('b')[0].text)
                    else:
                        nameFile = formatText(trNames[x].text)

                    nameFileFinal = "../Pokemon/Diferentes Formas/" + str(
                        number) + "-" + namePokemon + " - " + nameFile + ".png"

                    if not os.path.exists(nameFileFinal):
                        page = urllink(urlPokemonDownload)
                        soup = BeautifulSoup(page.content, 'html.parser')
                        image = soup.find_all("div", class_=re.compile("^fullImageLink"))[0]
                        urlPokemonDownload = image.find_all('a')[0]['href']
                        downloadImage(nameFileFinal, urlPokemonDownload)
                    number = number + 1
                count = count + sum
            countTag = countTag + 1  # Para megas
    except NameError:
        print(NameError)


def loadPage3(namePokemon, urlPokemon):
    page = urllink(urlPokemon)
    soup = BeautifulSoup(page.content, 'html.parser')
    megaGiga = False

    if namePokemon.find("Mega-") != -1:
        megaGiga = True
        namePokemon = namePokemon.split("Mega-")[1]

    if namePokemon.find("Gigamax") != -1:
        megaGiga = True
        namePokemon = namePokemon.split("Gigamax")[0]

    images = soup.find_all("table", {"class": "radius10"})
    lenclass = len(images)

    if lenclass >= 3 and not megaGiga:
        loadForms(namePokemon, images[0], False)

    images = soup.find_all("table", class_=re.compile("evolucion"))
    images2 = soup.find_all("table", class_=re.compile("radius10 evolucion"))
    lenclass = len(images) - len(images2)

    if lenclass > 1:
        for x in range(0, lenclass - 1):
            loadForms(namePokemon, images[x], True)


def loadForms(namePokemon, image, megaGiga):
    global number
    tagDifferent = 1
    if megaGiga:
        tagDifferent = 0

    try:
        finddiv = ""
        allTr = image.find_all("tr")
        length = len(allTr) - tagDifferent
        sum = 0

        if length < 5:
            finddiv = "td"
            sum = length

        if length % 6 == 0:
            finddiv = "td"
            sum = 6

        if length % 5 == 0:
            finddiv = "td"
            sum = 5

        if namePokemon == "Arceus":
            finddiv = "th"
            sum = 4

        if namePokemon == "Necrozma":
            finddiv = "td"
            sum = 4

        if namePokemon == "Minior":
            finddiv = "td"
            sum = 3

        if sum == 0:
            sum = 0

        count = 0
        while count < length:  # Filas: Ejemplo con los arceus
            tdLinks = allTr[count].find_all('td', class_=None)
            trNames = []

            if namePokemon == "Necrozma" or megaGiga:
                tdLinks = image.find_all('td', class_=None)
            else:
                trNames = allTr[count + 1].find_all(finddiv)

            for x in range(0, len(tdLinks)):
                urlPokemonDownload = base + tdLinks[x].find_all('a')[0]['href']

                if urlPokemonDownload in listUrlPokemonImage:
                    continue

                if namePokemon == "Necrozma" and x == 4:
                    continue

                if namePokemon == "Necrozma" or megaGiga:
                    if urlPokemonDownload == base + "/wiki/Archivo:Necrozma_HOME.png":
                        nameFile = formatText(tdLinks[x].find_all('a')[1].text)
                    else:
                        allB = tdLinks[x].find_all('b')
                        if len(allB) != 0:
                            nameFile = formatText(allB[0].text)
                        else:
                            nameFile = formatText(tdLinks[x].find_all('a')[1].text)

                else:
                    nameFile = formatText(trNames[x].text)

                if (nameFile not in listFormPokemon and
                        namePokemon != "Arceus" and
                        namePokemon != "Necrozma"and
                        namePokemon != "Minior" and
                        namePokemon != "Zacian" and
                        namePokemon != "Zamazenta"):
                    continue

                listUrlPokemonImage.append(urlPokemonDownload)
                nameFileFinal = "../Pokemon/Diferentes Formas/" + str(number) + "-" + namePokemon + " - " + nameFile + ".png"

                if not os.path.exists(nameFileFinal):
                    page = urllink(urlPokemonDownload)
                    soup = BeautifulSoup(page.content, 'html.parser')
                    image = soup.find_all("div", class_=re.compile("^fullImageLink"))[0]
                    urlPokemonDownload = image.find_all('a')[0]['href']
                    downloadImage(nameFileFinal, urlPokemonDownload)
                number = number + 1
            count = count + sum
    except NameError:
        print(NameError)


def downloadImage(nameFile, urlPokemonDownload):
    response = urllink(urlPokemonDownload)
    file = open(nameFile, "wb")
    file.write(response.content)
    file.close()


def downloadFormas():
    prevType = -1
    for x in range(0, len(listUrlPokemon)):
        if listNumberPokemon[x] == prevType:
            continue
        prevType = listNumberPokemon[x]
        loadPage3(listNamePokemon[x], listUrlPokemon[x])


def anadirDiferentesFormas():
    url = base + '/wiki/Lista_de_Pokémon_con_diferentes_formas'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    divs = soup.find_all("div", class_=re.compile("^cajaflexible"))
    numberType = 0

    for div in divs:
        divsMax = div.find_all('div', class_=re.compile("^float-app"))
        for divMax in divsMax:
            allDivs = divMax.find_all('div')

            if len(allDivs) >= 4:
                divType = allDivs[3].text
            else:
                divType = allDivs[0].text

            divName = allDivs[0].text
            url = base + divMax.find_all('a')[0]['href']
            if divType not in listFormPokemon or divName == "Darmanitan":
                listUrlPokemon.append(url)
                listNamePokemon.append(divName)
                listFormPokemon.append(divType)
                listNumberPokemon.append(numberType)
            if divName.find("Mega-") != -1 or divName.find("Gigamax") != -1:
                numberType = numberType + 1
        numberType = numberType + 1


def listaPokemonDiferentesFormas2():
    url = base + '/wiki/Lista_de_Pokémon_con_diferentes_formas'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    tables = soup.find_all("table", class_=re.compile("^galeria"))
    for table in tables:
        tr = table.find_all('tr', class_=re.compile("^encabezado"))[0]
        print(tr.text)


def formatText(text):
    return text.replace('\n', '')


def urllink(url):
    try:
        return requests.get(url)
    except:
        return urllink(url)


base = 'https://www.wikidex.net'
listNamePokemon = list()
listFormPokemon = list()
listNumberPokemon = list()
listUrlPokemon = list()
listUrlPokemonImage = list()
listLocationRed = list()
number = 1
title = "..\\Excel\\Pokemon-Ubicacion.xlsx"
# listaPokemon()
#anadirDiferentesFormas()
#downloadFormas()
# listaPokemonDiferentesFormas2()


