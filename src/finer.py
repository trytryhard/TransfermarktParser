"""Module with helpful non categorised small functions"""

import re


def link_finer(val: str) -> tuple:
    """
    :param val: string with club id on transfermarkt
    :return: corrected link with last actual squad or raise error
    """
    try:
        val = re.findall(r"\d+", val)[0]
        return ("https://www.transfermarkt.com/defualt/startseite/verein/" + val, val)
    except Exception as exc:
        print(
            f"Your input: {val}\n",
            "It should contains digit-identificator of club",
            r"like this: https://www.transfermarkt.com/sokol-saratov/startseite/verein/3834 \n",
        )
        raise NameError("Wrong team link!") from exc


def pos_finer(val: str) -> str:
    """
    :param val: long-name of position
    :return res: short-name of position
    """
    help_dict = {
        "Goalkeeper": "GK",
        "Defender": "DEF",
        "Midfield": "MID",
        "Attack": "ATK",
    }

    if val in help_dict:
        return help_dict[val]

    return val
