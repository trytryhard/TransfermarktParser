import json

from parser import Parse
from selenium import webdriver
from selenium.webdriver.common.by import By

#q = Parse('https://www.transfermarkt.com/ska-khabarovsk/startseite/verein/3690')
q = Parse('https://www.transfermarkt.world/nosta-novotroitsk/startseite/verein/11135/saison_id/2025')
q.listOfTeamMembers()
q.getPlayerAPI()
print(q.playersDict)

#print(q.listOfTeamMembers())
'''
def test(link):
    options = webdriver.ChromeOptions()
    options.page_load_strategy = 'eager'
    options.add_argument('--ignore-ssl-errors=yes')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--headless=new')

    driver = webdriver.Chrome(options=options)

    driver.get(link)

    #print(driver.page_source)

    jsonValue = json.loads(driver.find_element(By.CSS_SELECTOR,'pre').text)

    if jsonValue['success'] == True:
        print( jsonValue['data']['marketValueDetails']['current'] )

    return 1

print(test('https://tmapi-alpha.transfermarkt.technology/player/746440'))
'''