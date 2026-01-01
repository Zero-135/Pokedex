import os
import re
import datetime

import openpyxl
import pyodbc
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl.styles import Alignment


def listaPokemonUbicacion():
    global placesSpace
    url = base + '/wiki/List_of_Pokémon_by_National_Pokédex_number'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    gen = 1
    rowspan = 1

    tables = soup.find_all("table", class_=re.compile("^roundy"))
    for table in tables:
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            numberTds = len(tds)
            if numberTds == 0:  # or numberTds == 1 or numberTds == 2
                continue

            if rowspan > 1:
                rowspan = rowspan - 1
                continue

            urlPokemon = base + (tds[2].find_all('a'))[0]['href']
            namePokemon = formatText((tds[2].find_all('a'))[0].getText())
            numberPokemon = formatText(tds[0].text)
            old_gen = gen

            if "Alolan" in namePokemon:
                gen = 7
            if "Galarian" in namePokemon:
                gen = 8
            if "Hisuian" in namePokemon:
                gen = 8
            if "Paldean" in namePokemon:
                gen = 9

            placesSpace = getPlaces(gen)
            loadPagePokemon(numberPokemon, namePokemon, urlPokemon, gen)
            gen = old_gen
            rowspan = int(tds[0]['rowspan'])
        gen = gen + 1


def loadPagePokemon(numberPokemon, namePokemon, urlPokemon, gen):
    global placesSpace
    page = urllink(urlPokemon)
    soup = BeautifulSoup(page.content, 'html.parser')

    try:
        tagText = soup.find_all("span", string="Game data")[1]
        parent = tagText.parent
        print(namePokemon)
        siblings = parent.find_next_siblings("table", attrs={'class': 'roundy'}, recursive=False)
        if len(siblings) == 0:
            parent = parent.find_next_siblings("section", attrs={'class': 'mf-section-2'}, recursive=False)[0]
            tableLocation = parent.findChildren("table", attrs={'class': 'roundy'}, recursive=False)[1]
        else:
            tableLocation = parent.find_next_siblings("table", attrs={'class': 'roundy'}, recursive=False)[1]
        # tableLocation = tagText.findAll(
        # "table",  attrs={'class': 'roundy'}, recursive=False
        # )[2]#me traigo la tabla de localizaciones

        numbertr = 0
        listNumberPokemon.append(numberPokemon)
        listNamePokemon.append(namePokemon)
        listUrlPokemon.append(urlPokemon)

        trs = (tableLocation.findChildren('tbody', recursive=False)[0]).findChildren('tr', recursive=False)
        # me traigo la tabla de localizaciones por generacion

        prevNameGame = ""
        for tr in trs:
            if "This Pokémon was unavailable prior to Generation" in tr.getText():
                continue
            rowGames = (tr.find_all("table", style=re.compile("^background:#FFF; padding:3px;"))[0]
            .findChildren('tbody', recursive=False)[0]).findChildren('tr', recursive=False)
            numberGameGen = 1
            for game in rowGames:

                if (gen == 3 and (numberGameGen == 6 or numberGameGen == 7)) or \
                        (gen == 4 and (numberGameGen == 6)) or \
                        (gen == 5 and (numberGameGen == 5)):
                    continue

                versionsList = game.find_all('th', recursive=False)
                numberversions = len(versionsList)

                textSimple = str(game.find_all('td')[0]).replace("<br/>", "\n")
                location = BeautifulSoup(textSimple, "html.parser").getText().rstrip().lstrip()

                for numberV in range(numberversions):
                    nameGame = versionsList[numberV].extract().text.rstrip().lstrip()

                    rang = 0
                    if prevNameGame == "Sword Expansion Pass" and nameGame == "Brilliant Diamond":
                        rang = 1
                    if prevNameGame == "Shield" and nameGame == "Shield Expansion Pass":
                        rang = 1
                    if prevNameGame == "Shield" and nameGame == "Brilliant Diamond":
                        rang = 2
                    if prevNameGame == "Violet" and nameGame == "The Hidden Treasure of Area Zero (Violet)":
                        rang = 1
                    if nameGame == "Legends: Z-A":
                        continue
                    for dlc in range(rang):
                        numbertr = numbertr + 1

                    rang = 1
                    if nameGame == "Expansion Pass":
                        rang = 2
                    if nameGame == "The Hidden Treasure of Area Zero":
                        rang = 2
                    for dlc in range(rang):
                        appendLocation_SQL(numberPokemon, namePokemon, urlPokemon, numbertr + placesSpace, location)
                        numbertr = numbertr + 1
                        numberGameGen = numberGameGen + 1
                        prevNameGame = nameGame
            gen = gen + 1
    except NameError:
        print(NameError)


def getExcel():
    global title
    df = pd.DataFrame({"Numero": listNumberPokemon,
                       "Nombre": listNamePokemon,
                       "Red": listLocationRed,
                       "Blue": listLocationBlue,
                       #"Blue-Japan": listLocationBlueJapan,
                       "Yellow": listLocationYellow,
                       "Gold": listLocationGold,
                       "Silver": listLocationSilver,
                       "Crystal": listLocationCrystal,
                       "Ruby": listLocationRuby,
                       "Sapphire": listLocationSapphire,
                       "Emerald": listLocationEmerald,
                       "FireRed": listLocationFireRed,
                       "LeafGreen": listLocationLeafGreen,
                       "Diamond": listLocationDiamond,
                       "Pearl": listLocationPearl,
                       "Platinum": listLocationPlatinum,
                       "HeartGold": listLocationHeartGold,
                       "SoulSilver": listLocationSoulSilver,
                       "Black": listLocationBlack,
                       "White": listLocationWhite,
                       "Black 2": listLocationBlack2,
                       "White 2": listLocationWhite2,
                       "X": listLocationX,
                       "Y": listLocationY,
                       "Ruby Omega": listLocationRubyOmega,
                       "Sapphire Alpha": listLocationSapphireAlpha,
                       "Sun": listLocationSun,
                       "Moon": listLocationMoon,
                       "Ultra Sun": listLocationUltraSun,
                       "Ultra Moon": listLocationWUltraMoon,
                       "Let's Go Pikachu": listLocationLetsPik,
                       "Let's Go Eevee": listLocationLetsEev,
                       "Sword": listLocationSword,
                       "Shield": listLocationShield,
                       "Sword DLC": listLocationSwordDLC,
                       "Shield DLC": listLocationShieldDLC,
                       "Brilliant Diamond": listLocationBrillDia,
                       "Shining Pearl": listLocationShinPear,
                       "Legends: Arceus": listLocationLeyendA,
                       "Scarlet": listLocationScarlet,
                       "Violet": listLocationViolet,
                       "Scarlet DLC": listLocationScarletDLC,
                       "Violet DLC": listLocationVioletDLC,
                       "Url": listUrlPokemon,
                       })
    df.to_excel(title, index=False)

    wb = openpyxl.load_workbook(filename=title)
    worksheet = wb['Sheet1']
    worksheet.title = 'Ubicaciones'

    for col in worksheet.columns:
        max_length = 0
        column = col[0].column_letter  # Get the column name
        k = 1
        for cell in col:
            if column == "B" and k != 1:
                worksheet[column + str(k)].hyperlink = worksheet["AR" + str(k)].value
            worksheet[column + str(k)].alignment = Alignment(wrapText=True)
            try:  # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
            k = k + 1
        # adjusted_width = (max_length + 2) * 1.2
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column].width = adjusted_width
    worksheet.delete_cols(44, 1)
    worksheet.auto_filter.ref = worksheet.dimensions
    wb.save(title)
    os.system(title)


def urllink(url):
    try:
        return requests.get(url)
    except:
        return urllink(url)


def formatText(text):
    return text.replace('\n', '')


def getPlaces(gen):
    match gen:
        case 1:
            return (0)
        case 2:
            return (4)
        case 3:
            return (7)
        case 4:
            return (12)
        case 5:
            return (17)
        case 6:
            return (21)
        case 7:
            return (25)
        case 8:
            return (31)
        case 9:
            return (38)


def appendLocation_SQL(numberPokemon, namePokemon, urlPokemon, numberTr, location):
    game = ''
    match numberTr:
        case 0:
            game = 'R'
        case 1:
            game = 'BL'
        case 2:
            game = 'BJ'
        case 3:
            game = 'YE'
        case 4:
            game = 'G'
        case 5:
            game = 'S'
        case 6:
            game = 'C'
        case 7:
            game = 'RUB'
        case 8:
            game = 'SAP'
        case 9:
            game = 'E'
        case 10:
            game = 'FR'
        case 11:
            game = 'LG'
        case 12:
            game = 'D'
        case 13:
            game = 'P'
        case 14:
            game = 'PT'
        case 15:
            game = 'HG'
        case 16:
            game = 'SS'
        case 17:
            game = 'B'
        case 18:
            game = 'W'
        case 19:
            game = 'B2'
        case 20:
            game = 'W2'
        case 21:
            game = 'X'
        case 22:
            game = 'Y'
        case 23:
            game = 'RO'
        case 24:
            game = 'SA'
        case 25:
            game = 'SU'
        case 26:
            game = 'MO'
        case 27:
            game = 'USU'
        case 28:
            game = 'UMO'
        case 29:
            game = 'LP'
        case 30:
            game = 'LE'
        case 31:
            game = 'SW'
        case 32:
            game = 'SH'
        case 33:
            game = 'SWDLC'
        case 34:
            game = 'SHDLC'
        case 35:
            game = 'BD'
        case 36:
            game = 'SP'
        case 37:
            game = 'A'
        case 38:
            game = 'SC'
        case 39:
            game = 'VI'
        case 40:
            game = 'SCDLC'
        case 41:
            game = 'VIDLC'

    query = ("insert into pokelocationGame values('" +
             numberPokemon + "',N'" +
             namePokemon.replace("'", "''") + "','" +
             urlPokemon + "',N'" +
             location.replace("'", "''").replace('\n', ', ') + "','" +
             game + "')"
             )
    cursor.execute(query)
    conn.commit()


base = 'https://bulbapedia.bulbagarden.net'
placesSpace = 0
listNumberPokemon = list()
listNamePokemon = list()
listUrlPokemon = list()
listLocationRed = list()
listLocationBlue = list()
listLocationBlueJapan = list()
listLocationYellow = list()
listLocationGold = list()
listLocationSilver = list()
listLocationCrystal = list()
listLocationRuby = list()
listLocationSapphire = list()
listLocationEmerald = list()
listLocationFireRed = list()
listLocationLeafGreen = list()
listLocationDiamond = list()
listLocationPearl = list()
listLocationPlatinum = list()
listLocationHeartGold = list()
listLocationSoulSilver = list()
listLocationBlack = list()
listLocationWhite = list()
listLocationBlack2 = list()
listLocationWhite2 = list()
listLocationX = list()
listLocationY = list()
listLocationRubyOmega = list()
listLocationSapphireAlpha = list()
listLocationSun = list()
listLocationMoon = list()
listLocationUltraSun = list()
listLocationWUltraMoon = list()
listLocationLetsPik = list()
listLocationLetsEev = list()
listLocationSword = list()
listLocationShield = list()
listLocationSwordDLC = list()
listLocationShieldDLC = list()
listLocationBrillDia = list()
listLocationShinPear = list()
listLocationLeyendA = list()
listLocationScarlet = list()
listLocationViolet = list()
listLocationScarletDLC = list()
listLocationVioletDLC = list()
title = "..\\Excel\\Pokemon-Ubicacion_" + datetime.date.today().strftime("%d_%m_%Y") + ".xlsx"

server = '(LocalDb)\\MSSQLLocalDB'
bd = 'LocationPokemon'
try:
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER=' + server + ';DATABASE=' + bd +
                          ';Integrated Security=True')
    cursor = conn.cursor()
    cursor.execute("truncate table pokelocationGame")
    conn.commit()
except:
    print("Error")

listaPokemonUbicacion()
getExcel()
