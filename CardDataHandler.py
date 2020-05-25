# -*- coding:utf-8 -*-

from functools import lru_cache
import requests
from urllib.parse import quote_plus
from Util import process_string, timing
from pyquery import PyQuery as pq
from DatabaseHandler import getClosestTCGCardname
from ErrorMailer import SendErrorMail
import traceback
import re
import pprint
import difflib

WIKI_URL = 'https://yugipedia.com/wiki/'
TCG_BASE_URL = 'http://yugiohprices.com/api'
OCG_BASE_URL = 'https://yugipedia.com/api.php'

BREAK_TOKEN = '__BREAK__'

def sanitiseCardname(cardname):
    return cardname.replace('/', '%2F')

@lru_cache(maxsize=128)
def getOCGCardURL(searchText):
    try:
        searchResults = requests.get(OCG_BASE_URL + '?action=query&list=search&srsearch=' + searchText + '&srlimit=50&format=json')
    except Exception as e:
        SendErrorMail(e, traceback.format_exc())
        return None

    data = searchResults.json()['query']['search']

    titles = [item['title'].lower() for item in data]

    results = difflib.get_close_matches(searchText.lower(), titles, 1, 0.85)

    if results:
        for item in data:
            if item['title'].lower() == results[0]:
                return getWikiaURL(item['title']) 

    return None

def getOCGCardData(url):
    try:
        html = requests.get(url)
        ocg = pq(html.text)

        cardtable = list(ocg('table[class="innertable"]')('tbody').items('tr'))

        print("In getOCGCardData")

        data = {
            'image': ocg('div[class="cardtable-main_image-wrapper"]')('a img').attr["src"],
            'name': ocg('h1[id="firstHeading"]').text(),
            'type': cardtable[0]('td p a').attr["title"]
        }

        if (data['type'] == 'Monster Card'):
            data['monster_attribute'] = cardtable[1]('td p a').attr["title"]

            data['monster_types'] = [monster_type.text().strip() for monster_type in cardtable[2]('td p').items("a")]

            if 'Link' in data['monster_types']:
                data['monster_level'] = '/'.join([linkarrow.text() for linkarrow in list(cardtable[3]('td div').items("div"))[0].items("a")][8:])
            else:
                data['monster_level'] = int(list(cardtable[3]('td p').items("a"))[0].text())

            if 'Pendulum' in data['monster_types']:
                data['pendulum_scale'] = int(list(cardtable[4]('td p').items("a"))[1].text())
                atk_def = [value.text() for value in cardtable[5]('td p').items("a")]
            else:
                data['pendulum_scale'] = None
                atk_def = [value.text() for value in cardtable[4]('td p').items("a")]
     
            data['monster_attack'] = process_string(atk_def[0])
            data['monster_defense'] = process_string(atk_def[1])
     
        elif (data['type'] == 'Spell Card' or data['type'] == 'Trap Card'):
            data['spell_trap_property'] = list(cardtable[1]('td p').items("a"))[0].text()

        if (data['type'] == 'Monster Card'):
            for i, m_type in enumerate(data['monster_types']):
                data['monster_types'][i] = data['monster_types'][i].strip()

        description_element = cardtable[-1]('td div').html()
        description_element = re.sub(r'</dt>', ': </dt>' + BREAK_TOKEN, description_element)
        description_element = re.sub(r'</dd>', '</dd>' + BREAK_TOKEN, description_element)
        description_element = re.sub(r'<br ?/?>', BREAK_TOKEN, description_element)
        description_element = re.sub(r'<a href=[^>]+>', '', description_element)
        description_element = re.sub(r'</a>', '', description_element)
        description_element = pq(description_element).text()
        description_element = description_element.replace(BREAK_TOKEN, '\n')
        description_element = re.sub(r':(?=\w)', ': ', description_element)
        data['description'] = re.sub(r'\.(?=\w)', '. ', description_element)

        return data
        
    except Exception as e:
        SendErrorMail(e, traceback.format_exc())
        return None

def getPricesURL(cardName):
    return "http://yugiohprices.com/card_price?name=" + cardName.replace(" ", "+")

def getWikiaURL(cardName):
    return WIKI_URL + cardName.replace(" ", "_")

def formatOCGData(data):
    try:
        formatted = {}
        
        formatted['name'] = data['name']
        formatted['wikia'] = getWikiaURL(data['name'])
        formatted['pricedata'] = getPricesURL(data['name'])
        formatted['image'] = data['image']
        formatted['text'] = data['description'].replace('\n', '  \n')
        formatted['cardtype'] = data['type']
        
        if formatted['cardtype'] == 'Monster Card':
            formatted['attribute'] = data['monster_attribute'].upper()
            formatted['types'] = data['monster_types']

            formatted['level'] = data['monster_level']
            formatted['att'] = data['monster_attack']
            formatted['defn_type'] = 'DEF'
            formatted['def'] = data['monster_defense']

            formatted['pendulum_scale'] = data['pendulum_scale']

            if 'link' in ' '.join(str(i[1]).lower() for i in enumerate(formatted['types'])):
                formatted['leveltype'] = 'Link Arrows'
                formatted['defn_type'] = 'LINK'
            elif 'xyz' in ' '.join(str(i[1]).lower() for i in enumerate(formatted['types'])):
                formatted['leveltype'] = 'Rank'
            else:
                formatted['leveltype'] = 'Level'
        else:
            formatted['property'] = data['spell_trap_property']

        return formatted
    except Exception as e:
        SendErrorMail(e, traceback.format_exc())
        return None

def getCardData(searchText):
    try:
        print('Searching Yugipedia for: ' + searchText)
        wikiURL = getOCGCardURL(searchText)

        if not wikiURL:
            wikiURL = getWikiaURL(searchText)
            
        if (wikiURL):
            ocgData = getOCGCardData(wikiURL)
            formattedData = formatOCGData(ocgData)

            if formattedData:
                print("(OCG) Found: " + ocgData['name'])
                return formattedData
            else:
                return None
    except Exception as e:
        SendErrorMail(e, traceback.format_exc())
        return None
