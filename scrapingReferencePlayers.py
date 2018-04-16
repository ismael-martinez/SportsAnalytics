#Purpose: To parse the x-Reference.com site and retrieve player data.
import requests
from bs4 import BeautifulSoup
import bs4
from lxml import etree, html
import datetime
import os

def getPlayerUrls(baseUrl):
    # URL
    baseUrl = "https://www.basketball-reference.com"
    alphabet = ['a','b','c','d','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z']
    playersHrefList = []
    for letter in alphabet:
        fullUrl = baseUrl + "/players/" + letter + '/'
        letterPlayers = requests.get(fullUrl).text
        # Get players in bold
        soup = BeautifulSoup(letterPlayers, 'lxml')
        active_players = soup.find_all('strong')
        for el in active_players:
            if(el.find('a')):
                playersHrefList.append(baseUrl + el.find('a').get('href'))

    return playersHrefList

def scrapePlayerPage(url, start_year, end_year):
    r = requests.get(url)
    player_id = url.split('/')[-1]
    player_id = player_id.replace('.html', '')

    # Remove comment tags
    html = r.text.replace("<!--", "").replace("-->", "")

    soup = BeautifulSoup(html, 'lxml')
    # Get active years
    #years = []
    #for y in range(start_year, end_year+1):
    #    idy = 'per_game.' + str(y)
    #    if(soup.find(id=idy)):
    #        years.append(y)

    # Start data dictionary
    allData = {}
    allData['playerId'] = player_id

    # Get Data and write to CSV file
    tables = soup.find_all('table')
    allData['tables'] = []
    for table in tables:
        if(table.find('thead') and table.find('tbody') and table.get('id')):
            table_id = table.get('id')
            if not os.path.exists('data'):
                os.makedirs('data')
            if not os.path.exists('data\\' + table_id):
                os.makedirs('data\\' + table_id)
            if not os.path.exists('data\\' + table_id + '\\players'):
                os.makedirs('data\\' + table_id + '\\players')
            dir = os.path.dirname(os.path.realpath(__file__))
            fileName = '\\'.join([dir, 'data', table_id, 'players', player_id]) + '.csv'

            tableData = {'tableId': table_id}
            with open(fileName, 'w') as file:
                header = table.find('thead')
                headerRows = header.find_all('tr')
                header = []
                for row in headerRows:
                    rowList = []
                    for el in row.find_all('th'):
                        if el.get('colspan'):
                            c = int(el.get('colspan'))
                            for i in range(c):
                                rowList.append(el.text)
                            #rowList.append(el.text + '{' + el.get('colspan') + '}')
                        else:
                            rowList.append(el.text)

                    header.append(rowList)
                zippedHeader = list(zip(*header))
                concatHeader = []
                for z in zippedHeader:
                    filteredZ = list(filter(None, list(z)))
                    concatHeader.append(' | '.join(filteredZ))
                file.write(', '.join(concatHeader) + '\n')
                tableData['header'] = concatHeader



                body = table.find('tbody')
                bodyRows = body.find_all('tr')
                bodyData = []
                for row in bodyRows:
                    rowList = []
                    for el in row.find_all(['th', 'td']):
                        rowList.append(el.text)
                    file.write(', '.join(rowList) + '\n')
                    bodyData.append(rowList)

                tableData['body'] = bodyData
        allData['tables'].append(tableData)
    return allData


def combineCSVs(dir, filename):
    masterFile = open(filename, 'w')
    header = False
    for player in os.listdir(dir):
        playerFile = open(dir + '\\' + player, 'r')
        rows = playerFile.readlines()
        if not header:
            headerRow = 'playerId, ' + rows[0]
            masterFile.write(headerRow)
            header = True
        for r in rows[1:]:
            playerId = player.split('.')[0]
            row = playerId + ', ' + r
            masterFile.write(row)
        #body = ''.join(rows[1:])
        #masterFile.write(body)




def main():
    now = datetime.datetime.now()
    start_year = now.year - 15
    end_year = now.year

    baseUrl = "https://www.basketball-reference.com"
    #playersHrefList = getPlayerUrls(baseUrl)

# Build master csv here

    #for link in playersHrefList:
        #allData = scrapePlayerPage(link, start_year, end_year)
        #print(allData)

    # Read all files and create a master file
    dir = os.getcwd() + '\\data'
    for chdir in os.listdir(dir):
        combineCSVs(dir + '\\' + chdir + '\\players', dir + '\\' + chdir + '\\master.csv')

if __name__ == "__main__":
    main()