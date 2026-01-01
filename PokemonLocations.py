import os
import re

import openpyxl
import requests
from bs4 import BeautifulSoup
import pandas as pd
from openpyxl.styles import Alignment


def listaPokemonUbicacion():
    global placesSpace
    url = base + '/wiki/Lista_de_Pokémon'
    page = urllink(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    gen = 1

    tables = soup.find_all("table", class_=re.compile("^tabpokemon"))
    for table in tables:
        trs = table.find_all('tr')
        for tr in trs:
            tds = tr.find_all('td')
            numberTds = len(tds)
            if numberTds == 0 or numberTds == 1 or numberTds == 2:
                continue

            if numberTds == 4:
                name = 1
            else:
                name = 0

            urlPokemon = base + (tds[name].find_all('a'))[0]['href']
            namePokemon = formatText(tds[name].text)
            old_gen = gen

            if "Alola" in namePokemon:
                gen = 7
            if "Galar" in namePokemon:
                gen = 8
            if "Hisui" in namePokemon:
                gen = 8
            if "Paldea" in namePokemon:
                gen = 9

            placesSpace = getPlaces(gen)
            loadPagePokemon(namePokemon, urlPokemon)
            gen = old_gen
        gen = gen + 1


def loadPagePokemon(namePokemon, urlPokemon):
    global placesSpace
    page = urllink(urlPokemon)
    soup = BeautifulSoup(page.content, 'html.parser')

    try:
        tableLocation = soup.find_all("table", class_=re.compile("^localizacion"))[0]

        trs = tableLocation.find_all('tr')
        first = True
        numbertr = 0
        listNamePokemon.append(namePokemon)
        listUrlPokemon.append(urlPokemon)

        for number in range(placesSpace):
            appemdLocation(number, "")

        for tr in trs:
            if first:
                first = False
                continue

            location = tr.find_all('td')[0].extract().text.rstrip().lstrip()
            appemdLocation(numbertr + placesSpace, location)

            numbertr = numbertr + 1

    except NameError:
        print(NameError)


def getExcel():
    global title
    df = pd.DataFrame({"Nombre": listNamePokemon,
                       "Red": listLocationRed,
                       "Blue": listLocationBlue,
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
                       "Brilliant Diamond": listLocationBrillDia,
                       "Shining Pearl": listLocationShinPear,
                       "Legends: Arceus": listLocationLeyendA,
                       "Scarlet": listLocationScarlet,
                       "Violet": listLocationViolet,
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
            if column == "A" and k != 1:
                worksheet[column + str(k)].hyperlink = worksheet["AM" + str(k)].value
            worksheet[column + str(k)].alignment = Alignment(wrapText=True)
            try:  # Necessary to avoid error on empty cells
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
            k = k + 1
        #adjusted_width = (max_length + 2) * 1.2
        adjusted_width = (max_length + 2)
        worksheet.column_dimensions[column].width = adjusted_width
    worksheet.delete_cols(39, 1)
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
            return(0)
        case 2:
            return(3)
        case 3:
            return(6)
        case 4:
            return(11)
        case 5:
            return (16)
        case 6:
            return (20)
        case 7:
            return (24)
        case 8:
            return (30)
        case 9:
            return (35)



def appemdLocation(numberTr, location):
    match numberTr:
        case 0:
            listLocationRed.append(location)
        case 1:
            listLocationBlue.append(location)
        case 2:
            listLocationYellow.append(location)
        case 3:
            listLocationGold.append(location)
        case 4:
            listLocationSilver.append(location)
        case 5:
            listLocationCrystal.append(location)
        case 6:
            listLocationRuby.append(location)
        case 7:
            listLocationSapphire.append(location)
        case 8:
            listLocationEmerald.append(location)
        case 9:
            listLocationFireRed.append(location)
        case 10:
            listLocationLeafGreen.append(location)
        case 11:
            listLocationDiamond.append(location)
        case 12:
            listLocationPearl.append(location)
        case 13:
            listLocationPlatinum.append(location)
        case 14:
            listLocationHeartGold.append(location)
        case 15:
            listLocationSoulSilver.append(location)
        case 16:
            listLocationBlack.append(location)
        case 17:
            listLocationWhite.append(location)
        case 18:
            listLocationBlack2.append(location)
        case 19:
            listLocationWhite2.append(location)
        case 20:
            listLocationX.append(location)
        case 21:
            listLocationY.append(location)
        case 22:
            listLocationRubyOmega.append(location)
        case 23:
            listLocationSapphireAlpha.append(location)
        case 24:
            listLocationSun.append(location)
        case 25:
            listLocationMoon.append(location)
        case 26:
            listLocationUltraSun.append(location)
        case 27:
            listLocationWUltraMoon.append(location)
        case 28:
            listLocationLetsPik.append(location)
        case 29:
            listLocationLetsEev.append(location)
        case 30:
            listLocationSword.append(location)
        case 31:
            listLocationShield.append(location)
        case 32:
            listLocationBrillDia.append(location)
        case 33:
            listLocationShinPear.append(location)
        case 34:
            listLocationLeyendA.append(location)
        case 35:
            listLocationScarlet.append(location)
        case 36:
            listLocationViolet.append(location)


base = 'https://www.wikidex.net'
placesSpace = 0
listNamePokemon = list()
listUrlPokemon = list()
listLocationRed = list()
listLocationBlue = list()
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
listLocationBrillDia = list()
listLocationShinPear = list()
listLocationLeyendA = list()
listLocationScarlet = list()
listLocationViolet = list()
title = "..\\Excel\\Pokemon-Ubicacion.xlsx"

listaPokemonUbicacion()
getExcel()