"""Module with parser-engine"""

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
    """Parser for checking movement of squad value"""

    # class const attr
    URL_API_TEAM = r"https://tmapi-alpha.transfermarkt.technology/club/"
    URL_API_PLAYER = r"https://tmapi-alpha.transfermarkt.technology/player/"

    # object attrs
    def __init__(
        self,
        url: str = "https://www.transfermarkt.com/sokol-saratov/startseite/verein/3834",
    ):
        self._url, self._team_id = finer.link_finer(url)
        self._players_dict = {"id": {"full_name": "", "pos": "", "prev_price": 0, "curr_price": 0}}
        self.df = None
        self.temp_df = None
        self.team_name = ""

    def check_team_status(self) -> bool:
        """Checks appearance of team in data source (transfermarkt)"""
        options = webdriver.ChromeOptions()
        options.page_load_strategy = "eager"
        options.add_argument("--ignore-ssl-errors=yes")
        options.add_argument("--ignore-certificate-errors")
        options.add_argument("--headless=new")

        driver = webdriver.Chrome(options=options)

        driver.get(self.URL_API_TEAM + self._team_id)

        json_value = json.loads(driver.find_element(By.CSS_SELECTOR, "pre").text)

        if "success" not in json_value.keys():
            print("Wrong response from your link")
            raise NameError("Check method Parse.checkTeamStatus and status of _urlAPITeam")

        self.team_name = json_value["data"]["name"]

        if json_value["data"]["identifier"] == f"Retired ({self._team_id})":
            print(f"Wrong team url. Check existence of {self.team_name} ({self._team_id}) on Transfermarkt")
            raise NameError("Check existence of this team on Transfermarkt")

        if json_value["data"]["squadDetails"]["squadSize"] == 0:
            print(f"There is no players in - {self.team_name}")
            raise NameError("Please input team with players")

        return True

    def list_of_team_members(self) -> bool:
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

        time.sleep(1)
        source = BeautifulSoup(driver.page_source, features="html.parser")

        print(f"Workin with team : {self.team_name}")

        full_table_of_players = source.find("div", class_="grid-view")

        number_pos = []
        for i in full_table_of_players.find_all("td"):
            if re.match(r'<td class="zentriert rueckennummer', str(i)):
                i_temp = str(i)

                if len(re.findall(r"\d+", i_temp)) > 0:
                    number = re.findall(r"\d+", i_temp)[0]
                else:
                    number = "-"

                pos = i_temp.split('title="')[1].split('"')[0]
                pos = finer.pos_finer(pos)

                number_pos.append((number, pos))

        for i in full_table_of_players.find_all("a"):
            if re.match(r'<a href="\/.+spieler.+">', str(i)):
                temp_i = str(i)
                full_name = " ".join(temp_i.split("/")[1].split("-")).title()
                uid = re.findall(r"\d+", temp_i)[0]

                # frames data
                self._players_dict[uid] = {
                    "number": "",
                    "full_name": full_name,
                    "pos": "",
                    "currency": "",
                    "prev_price": 0,
                    "curr_price": 0,
                }

        del self._players_dict["id"]

        for i in self._players_dict.items():
            numb, pos = number_pos.pop(0)
            self._players_dict[i]["number"] = numb
            self._players_dict[i]["pos"] = pos

        return True

    def get_player_data_api(self) -> bool:
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

        for i in self._players_dict.items():
            driver.get(Parse.URL_API_PLAYER + i)
            json_value = json.loads(driver.find_element(By.CSS_SELECTOR, "pre").text)

            if "success" in json_value.keys() and "marketValueDetails" in json_value["data"].keys():
                # self._players_dict = {"id": {"full_name": "", "pos": "", "prev_price": 0, "curr_price": 0}}
                json_value = json_value["data"]["marketValueDetails"]
                json_mrkt_det = json_value["current"]["compact"]

                self._players_dict[i]["currency"] = json_mrkt_det["prefix"]
                self._players_dict[i]["curr_price"] = json_mrkt_det["content"] + json_mrkt_det["suffix"]

                if "previous" not in json_value:
                    self._players_dict[i]["prev_price"] = "-"
                    self._players_dict[i]["delta_val"] = "-"
                    self._players_dict[i]["delta_percent, %"] = "-"
                else:
                    json_mrkt_det = json_value["previous"]["compact"]
                    self._players_dict[i]["prev_price"] = json_mrkt_det["content"] + json_mrkt_det["suffix"]

                    json_mrkt_det = json_value["delta"]

                    self._players_dict[i]["delta_val"] = int(json_mrkt_det["value"].split()[0].replace(".", ""))
                    self._players_dict[i]["delta_percent, %"] = float(
                        json_mrkt_det["percentage"].split()[0].replace(",", ".")
                    )

            else:
                self._players_dict[i]["current_price"] = "-"
                self._players_dict[i]["last_price"] = "-"
                self._players_dict[i]["delta_val"] = "-"
                self._players_dict[i]["delta_percent, %"] = "-"

            self.df = pd.DataFrame.from_dict(self._players_dict, orient="index")
            self.df = self.df.replace("-", pd.NA)
            self.df["delta_val"] = pd.to_numeric(self.df["delta_val"], errors="coerce")
            self.df["delta_percent, %"] = pd.to_numeric(self.df["delta_percent, %"], errors="coerce")

        return True

    def work_with_pl_dict(self, cmd) -> bool:
        """
        :param cmd: way of work with temp_df (self.df)
        :return:
        """
        temp_df = self.df
        cmd = int(cmd)
        ascending_attr = bool(cmd % 2)

        # Sort by deltaVal
        if cmd in {1, 2}:
            self.temp_df = temp_df.sort_values("delta_val", ascending=ascending_attr)

        elif cmd in {3, 4}:
            self.temp_df = temp_df.sort_values("delta_percent, %", ascending=ascending_attr)

        elif cmd == 0:
            self.temp_df = temp_df
        return True

    def print_markdown_table(self) -> bool:
        """
        print resulted dataframe from workWithPlDict
        :return:
        """
        print(f"Team: {self.team_name}")
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

        return True
