import json
import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By

import finer

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.expand_frame_repr", False)


class Parse:
    # class const attr
    _urlAPITeam = r"https://tmapi-alpha.transfermarkt.technology/club/"
    _urlAPIPlayer = r"https://tmapi-alpha.transfermarkt.technology/player/"

    # object attrs
    def __init__(
        self,
        url: str = "https://www.transfermarkt.com/sokol-saratov/startseite/verein/3834",
    ):
        self._url, self._team_id = finer.linkFiner(url)
        self.playersDict = {"id": {"fullName": "", "pos": "", "prevPrice": 0, "currPrice": 0}}
        self.df = None
        self.temp_df = None
        self.teamName = ""

    def checkTeamStatus(self) -> bool:
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        driver.get(self._urlAPITeam + self._team_id)

        jsonValue = json.loads(driver.find_element(By.CSS_SELECTOR, "pre").text)

        if jsonValue["success"] != True:
            print("Wrong response from your link")
            raise NameError("Check method Parse.checkTeamStatus and status of _urlAPITeam")

        self.teamName = jsonValue["data"]["name"]

        if jsonValue["data"]["identifier"] == f"Retired ({self._team_id})":
            print(f"Wrong team url. Check existence of {self.teamName} ({self._team_id}) on Transfermarkt")
            raise NameError("Check existence of this team on Transfermarkt")

        if jsonValue["data"]["squadDetails"]["squadSize"] == 0:
            print(f"There is no players in - {self.teamName}")
            raise NameError("Please input team with players")

        return True

    def listOfTeamMembers(self) -> bool:
        """
        :param: string with club id on transfermarkt
        :return: bool of success
        """
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        driver.get(self._url)

        print("Please wait a second before data scraping")
        time.sleep(1)
        source = BeautifulSoup(driver.page_source, features="html.parser")

        print(f"Workin with team : {self.teamName}")

        fullTableOfPlayers = source.find("div", class_="grid-view")

        numberPos = []
        for i in fullTableOfPlayers.find_all("td"):
            if re.match(r'<td class="zentriert rueckennummer', str(i)):
                i_temp = str(i)
                try:
                    number = re.findall("\d+", i_temp)[0]
                except:
                    number = "-"

                pos = i_temp.split('title="')[1].split('"')[0]
                pos = finer.posFiner(pos)

                numberPos.append((number, pos))

        for i in fullTableOfPlayers.find_all("a"):
            if re.match('<a href="\/.+spieler.+">', str(i)):
                temp_i = str(i)
                fullName = " ".join(temp_i.split("/")[1].split("-")).title()
                uid = re.findall("\d+", temp_i)[0]

                # frames data
                self.playersDict[uid] = {
                    "number": "",
                    "fullName": fullName,
                    "pos": "",
                    "currency": "",
                    "prevPrice": 0,
                    "currPrice": 0,
                }

        del self.playersDict["id"]

        for i in self.playersDict:
            numb, pos = numberPos.pop(0)
            self.playersDict[i]["number"] = numb
            self.playersDict[i]["pos"] = pos

        return True

    def getPlayerDataAPI(self) -> bool:
        """
        works with self.playersDict and update it with actual data
        :return: bool of success
        """

        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        driver.get(self._url)

        time.sleep(1)

        for i in self.playersDict:
            driver.get(Parse._urlAPIPlayer + i)
            jsonValue = json.loads(driver.find_element(By.CSS_SELECTOR, "pre").text)

            if jsonValue["success"] == True and "marketValueDetails" in jsonValue["data"]:
                # self.playersDict = {'id': {'fullName': '', 'pos': '', 'prevPrice': 0, 'currPrice': 0}}
                jsonValue = jsonValue["data"]["marketValueDetails"]
                jsonMRKTDet = jsonValue["current"]["compact"]

                self.playersDict[i]["currency"] = jsonMRKTDet["prefix"]
                self.playersDict[i]["currPrice"] = jsonMRKTDet["content"] + jsonMRKTDet["suffix"]

                if "previous" not in jsonValue:
                    self.playersDict[i]["prevPrice"] = "-"
                    self.playersDict[i]["deltaVal"] = "-"
                    self.playersDict[i]["deltaPercent, %"] = "-"
                else:
                    jsonMRKTDet = jsonValue["previous"]["compact"]
                    self.playersDict[i]["prevPrice"] = jsonMRKTDet["content"] + jsonMRKTDet["suffix"]

                    jsonMRKTDet = jsonValue["delta"]

                    self.playersDict[i]["deltaVal"] = int(jsonMRKTDet["value"].split()[0].replace(".", ""))
                    self.playersDict[i]["deltaPercent, %"] = float(
                        jsonMRKTDet["percentage"].split()[0].replace(",", ".")
                    )

            else:
                self.playersDict[i]["currentPrice"] = "-"
                self.playersDict[i]["lastPrice"] = "-"
                self.playersDict[i]["deltaVal"] = "-"
                self.playersDict[i]["deltaPercent, %"] = "-"

            self.df = pd.DataFrame.from_dict(self.playersDict, orient="index")
            self.df = self.df.replace("-", pd.NA)
            self.df["deltaVal"] = pd.to_numeric(self.df["deltaVal"], errors="coerce")
            self.df["deltaPercent, %"] = pd.to_numeric(self.df["deltaPercent, %"], errors="coerce")

        return True

    def workWithPlDict(self, cmd) -> bool:
        """
        :param cmd: way of work with temp_df (self.df)
        :return:
        """
        temp_df = self.df
        cmd = int(cmd)
        ascendingAttr = True if cmd % 2 == 1 else False

        # Sort by deltaVal
        if cmd in {1, 2}:
            self.temp_df = temp_df.sort_values("deltaVal", ascending=ascendingAttr)

        elif cmd in {3, 4}:
            self.temp_df = temp_df.sort_values("deltaPercent, %", ascending=ascendingAttr)

        elif cmd == 0:
            self.temp_df = temp_df

        return True

    def print_markdown_table(self):
        """
        print resulted dataframe from workWithPlDict
        :return:
        """
        print(f"Team: {self.teamName}")
        # widths
        col_widths = [max(len(str(val)) for val in self.temp_df[col].values) for col in self.temp_df.columns]
        col_widths = [max(w, len(col)) for w, col in zip(col_widths, self.temp_df.columns)]

        # head of table
        header = "| " + " | ".join(col.ljust(w) for col, w in zip(self.temp_df.columns, col_widths)) + " |"
        separator = "|-" + "-|-".join("-" * w for w in col_widths) + "-|"

        print(header)
        print(separator)

        # lines
        for _, row in self.temp_df.iterrows():
            line = "| " + " | ".join(str(val).ljust(w) for val, w in zip(row, col_widths)) + " |"
            print(line)
