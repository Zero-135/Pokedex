import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote


def urllink(url):
    try:
        return requests.get(url)
    except:
        return urllink(url)


def formatText(text):
    return text.replace('\n', '')


def listaPokemon():
    url = base + '/wiki/List_of_Pokémon_by_National_Pokédex_number'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("table", class_=re.compile("^roundy"))
    for table in tables:
        trs = table.find_all('tr')
        first = True
        for tr in trs:
            if first:
                first = not first
                continue

            tds = tr.find_all('td')
            number = tds[0].text.replace("#", "")

            if not number.isdigit():
                continue

            urlPokemon = base + (tds[1].find_all('a'))[0]['href']
            namePokemon = formatText((tds[2].find_all('a'))[0].text).replace(": ", "_")
            url_Image = base + "/wiki/File:" + number + quote(namePokemon) + ".png"

            nameFile = "../Pokemon/Bulbapedia/Pokedex Nacional/" + number + " - " + namePokemon + ".png"
            if not os.path.exists(nameFile):
                loadPage(nameFile, url_Image)


def loadPage(nameFile, urlPokemon):
    try:
        page = urllink(urlPokemon)
        soup = BeautifulSoup(page.content, 'html.parser')
        image = soup.find_all("div", class_=re.compile("^fullImageLink"))[0]
        urlPokemonDownload = image.find_all('a')[0]['href']

        downloadImage(nameFile, urlPokemonDownload)
    except NameError:
        print(NameError)


def downloadImage(nameFile, urlPokemonDownload):
    response = urllink(urlPokemonDownload)
    file = open(nameFile, "wb")
    file.write(response.content)
    file.close()


def listaPokemonForms():
    url = base + '/wiki/List_of_Pokémon_with_form_differences'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    divs = soup.find_all("div", class_=re.compile("^roundy"))
    number = 1
    for div in divs:

        namePokemon = (div.find_all("div")[0]).find_all("a")[0]['title'].split(' (Pokémon)')[0]

        listPokemonbyIndex = [name for name in getList("IndexPokemon.txt") if namePokemon in name]

        numberPokemon = ""
        if len(listPokemonbyIndex) > 0:
            numberPokemon = listPokemonbyIndex[0].split('#')[1]
        else:
            if namePokemon == "Starmobile":
                numberPokemon = "0966"
            else:
                numberPokemon = "0479"

        # if numberPokemon == "HOME":
        #     numberPokemon = (div.find_all("div")[0]).find_all("img")[0]['alt'][4:8]

        nameFullPokemon = (div.find_all("div")[0]).find_all("a")[0]['title'].replace(" (Pokémon)", "")
        nameTypePokemon = div.find_all("div")[0].text.replace("?", "_").replace(": ", "_")
        namePokemon = numberPokemon + "_" + str(number) + "_" + nameFullPokemon + " - " + nameTypePokemon

        if nameFullPokemon == "Arceus":
            namePokemon = namePokemon + div.find_all("div")[1].text.rstrip().lstrip()

        url_Image = (div.find_all('img'))[0]['src']
        url_Image = url_Image.replace("thumb/", "").rsplit("/", 1)[0]

        nameFile = "../Pokemon/Bulbapedia/Pokedex Diferentes Formas/" + namePokemon + ".png"
        if not os.path.exists(nameFile):
            downloadImage(nameFile, url_Image)
        number = number + 1


def listaPokemonRegional():
    url = base + '/wiki/Regional_form'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("table", class_=re.compile("^roundy"))
    number = 0
    namePokemon = ""
    form = ""
    for table in tables:
        trs = table.find_all('tr')[:-1]
        first = True
        for tr in trs:
            if first:
                first = not first
                continue

            tds = tr.find_all('td')
            ths = tr.find_all('th')
            cantTds = len(tds)
            cantThs = len(ths)

            if cantTds > 4:
                number = formatText(tds[0].text.replace("#", ""))
                namePokemon = formatText(tds[1].text)
                url_Image = (tds[3].find_all('img'))[0]['src']
                cantA = len(tds[3].find_all('a', recursive=False))
                if cantA == 1:
                    namePokemon = namePokemon + "-" + formatText((tds[3].find_all('a'))[1].text)
            else:
                plusnumber = 0
                if cantTds == 4:
                    plusnumber = 1
                cantA = len(tds[plusnumber].find_all('a', recursive=False))
                if cantA == 1:
                    namePokemon = namePokemon + "-" + formatText((tds[0].find_all('a'))[1].text)
                url_Image = (tds[plusnumber].find_all('img'))[0]['src']

            if cantThs > 0:
                form = (ths[0].find_all('a'))[1].text

            namePokemon = formatText(namePokemon.replace("?", "_").replace(": ", "_"))
            url_Image = url_Image.replace("thumb/", "").rsplit("/", 1)[0]

            nameFile = "../Pokemon/Bulbapedia/Pokedex Formas Regionales/" + str(
                number) + "-" + namePokemon + "-" + form + ".png"
            if not os.path.exists(nameFile):
                downloadImage(nameFile, url_Image)


def listaPokemonMega():
    url = base + '/wiki/Mega_Evolution'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("table", class_=re.compile("^roundy"))[:-3]
    limit = 2
    number = ""
    namePokemon = ""
    for table in tables:
        trs = table.find_all('tr')[:-1]
        row = 0
        for tr in trs:
            if row < limit:
                row = row + 1
                continue

            tds = tr.find_all('td')
            if len(tds) > 5:
                number = formatText(tds[0].text.replace("#", ""))
                urlPokemon = base + (tds[5].find_all('a'))[0]['href']
                namePokemon = formatText((tds[1].find_all('a'))[0].text).replace(": ", "_")
                listA = tds[8].find_all('a')
                cantSplit = []
                if len(listA) > 1:
                    cantSplit = formatText(listA[1].text).split(" ")

                if len(cantSplit) == 2:
                    namePokemon = namePokemon + " " + cantSplit[1]
            else:
                urlPokemon = base + (tds[0].find_all('a'))[0]['href']
                nameStone = formatText((tds[3].find_all('a'))[1].text).split(" ")[-1]
                namePokemon = namePokemon.split(" ")[0] + " " + nameStone
            nameFile = "../Pokemon/Bulbapedia/Pokedex Mega/" + number + "-" + namePokemon + ".png"
            if not os.path.exists(nameFile):
                loadPage(nameFile, urlPokemon)


def listaPokemonGigamax():
    url = base + '/wiki/Gigantamax'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("table", class_=re.compile("^roundy"))[:-1]
    limit = 2
    number = ""
    namePokemon = ""
    urlPokemon = ""
    for table in tables:
        trs = table.find_all('tr')[:-1]
        row = 0
        for tr in trs:
            if row < limit:
                row = row + 1
                continue

            tds = tr.find_all('td')
            ths = tr.find_all('th')
            if len(tds) > 5:
                number = formatText(tds[0].text.replace("#", ""))
                urlPokemon = base + (tds[5].find_all('a'))[0]['href']
                namePokemon = formatText(tds[1].text).replace(": ", "_")
                namePokemon = namePokemon + " " + formatText(ths[0].find_all('a')[0].text)
            else:
                if formatText(tds[0].text.replace("#", "")).isdigit():
                    number = formatText(tds[0].text.replace("#", ""))
                    namePokemon = formatText(tds[1].text).replace(": ", "_")
                else:
                    namePokemon = formatText(tds[0].text).replace(": ", "_")
                    urlPokemon = base + (tds[3].find_all('a'))[0]['href']
                namePokemon = namePokemon + " " + formatText(ths[0].find_all('a')[0].text)
            nameFile = "../Pokemon/Bulbapedia/Pokedex Gigamax/" + number + "-" + namePokemon + ".png"
            if not os.path.exists(nameFile):
                loadPage(nameFile, urlPokemon)


def listaPokemonIndexName():
    url = base + '/wiki/List_of_Pokémon_by_National_Pokédex_number'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    tables = soup.find_all("table", class_=re.compile("^roundy"))
    with open("IndexPokemon.txt", "w", encoding="utf-8") as f:
        for table in tables:
            trs = table.find_all('tr')
            first = True
            for tr in trs:
                if first:
                    first = not first
                    continue

                tds = tr.find_all('td')
                number = tds[0].text.replace("#", "")

                if not number.isdigit():
                    continue

                namePokemon = formatText((tds[2].find_all('a'))[0].text).replace(": ", "_")

                line = namePokemon + tds[0].text
                f.write(line + "\n")


def getList(rooth):
    my_file = open(rooth, "r", encoding="utf-8")
    data = my_file.read()
    my_file.close()
    return data.split("\n")


base = 'https://bulbapedia.bulbagarden.net'
# listaPokemonIndexName()
# listaPokemon()
# listaPokemonForms()
# listaPokemonRegional()
# listaPokemonMega()
# listaPokemonGigamax()
