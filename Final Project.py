#################################
##### Name:     Ziyu Wang
##### Uniqname: ziwa
#################################

from bs4 import BeautifulSoup
import requests
import json
import numpy as np


active_url = "https://finance.yahoo.com/most-active"
find_symbol_url = "https://finance.yahoo.com/most-active/?count=25&offset="
income_statement_url = "https://finance.yahoo.com/quote/XX/financials?p=XX"
balance_sheet_url = "https://finance.yahoo.com/quote/XX/balance-sheet?p=XX"
cash_flow_url = "https://finance.yahoo.com/quote/XX/cash-flow?p=XX"
CACHE_FILENAME = "url.json"
CACHE_FILENAME_1 = "info.json"
CACHE_DICT = {}
CACHE_DICT_1 = {}


class StockInfo:
    def __init__(self, debt_rate, ROE, profit_rate):
        self.debt_rate = debt_rate
        self.ROE = ROE
        self.profit_rate = profit_rate

    def info(self):
        if (self.debt_rate < 0.4) & (self.ROE > 0.2) & (self.profit_rate > 0.1):
            return True
        else:
            return False


def open_cache(name):
    ''' Opens the cache file if it exists and loads the JSON into
    the CACHE_DICT dictionary.
    if the cache file doesn't exist, creates a new cache dictionary

    Parameters
    ----------
    None

    Returns
    -------
    The opened cache: dict
    '''
    try:
        cache_file = open(name, 'r')
        cache_contents = cache_file.read()
        cache_dict = json.loads(cache_contents)
        cache_file.close()
    except:
        cache_dict = {}
    return cache_dict


def save_cache(cache_dict, name):
    ''' Saves the current state of the cache to disk

    Parameters
    ----------
    cache_dict: dict
        The dictionary to save

    Returns
    -------
    None
    '''
    dumped_json_cache = json.dumps(cache_dict)
    fw = open(name, "w")
    fw.write(dumped_json_cache)
    fw.close()


def build_symbol_dict():
    ''' Make a dictionary that maps stock symbols to stock page url from "yahoo finance most active"

    Parameters
    ----------
    None

    Returns
    -------
    dict
        key is a stock symbol and value is the url
        e.g. {'AAPL':'https://finance.yahoo.com/quote/AAPL/financials?p=AAPL', ...}
    '''
    symbol_list = []
    symbol_url_dict = {}
    CACHE_DICT = open_cache(CACHE_FILENAME)

    resp = requests.get(active_url)
    soup = BeautifulSoup(resp.text, "html.parser")

    # Find how many active stocks are there today
    # These changes frequently, no need to use CACHE
    total_num = soup.find(class_="Mstart(15px) Fw(500) Fz(s)").find("span").text.strip()
    num_begin = total_num.find("of")
    num_end = total_num.find("results")
    total_num = int(total_num[num_begin+3: num_end-1])

    # Add symbols and link to income statement url
    loop_num = int(total_num/25) + 1
    for i in range(loop_num):
        resp_1 = requests.get(find_symbol_url + str(i*25))
        soup_1 = BeautifulSoup(resp_1.text, "html.parser")

        for item in soup_1.select('.simpTblRow'):
            symbol = item.select('[aria-label=Symbol]')[0].get_text()
            if symbol in CACHE_DICT.keys():
                print("Using cache")
            else:
                print("Fetching")
                CACHE_DICT[symbol] = {}
                CACHE_DICT[symbol]["income_statement"] = income_statement_url.replace("XX", symbol)
                CACHE_DICT[symbol]["balance_sheet"] = balance_sheet_url.replace("XX", symbol)
                CACHE_DICT[symbol]["cash_flow"] = cash_flow_url.replace("XX", symbol)
                save_cache(CACHE_DICT, CACHE_FILENAME)

    return CACHE_DICT


def get_financial_info(symbol, symbol_dict):
    CACHE_DICT_1 = open_cache(CACHE_FILENAME_1)

    if symbol in CACHE_DICT_1.keys():
        print("Using cache")
    else:
        resp_1 = requests.get(symbol_dict[symbol]["balance_sheet"])
        soup_1 = BeautifulSoup(resp_1.text, "html.parser")

        ls_1 = []
        total_assets = []
        total_debt = []
        cash_row = soup_1.find_all(class_="D(tbr) fi-row Bgc($hoverBgColor):h")
        for i in cash_row:
            a = i.find_all("span")
            for b in a:
                ls_1.append(b.get_text())

        for i in range(len(ls_1)):
            if ls_1[i] == "Total Assets":
                for j in range(1, 3):
                    total_assets.append(int(ls_1[i+j].replace(",", "")))
            elif ls_1[i] == "Total Debt":
                for j in range(1, 3):
                    total_debt.append(int(ls_1[i+j].replace(",", "")))
        debt_rate = np.mean(total_debt) / np.mean(total_assets)

        resp_2 = requests.get(symbol_dict[symbol]["income_statement"])
        soup_2 = BeautifulSoup(resp_2.text, "html.parser")

        ls_2 = []
        total_revenue = []
        net_income = []
        stockholder_income = []
        ave_shares = []
        income = soup_2.find_all(class_="D(tbr) fi-row Bgc($hoverBgColor):h")
        for i in income:
            a = i.find_all("span")
            for b in a:
                ls_2.append(b.get_text())

        for i in range(len(ls_2)):
            if ls_2[i] == "Total Revenue":
                for j in range(2, 4):
                    total_revenue.append(int(ls_2[i + j].replace(",", "")))
            elif ls_2[i] == "Net Income from Continuing & Discontinued Operation":
                for j in range(2, 4):
                    net_income.append(int(ls_2[i + j].replace(",", "")))
            elif ls_2[i] == "Net Income Common Stockholders":
                for j in range(2, 4):
                    stockholder_income.append(int(ls_2[i + j].replace(",", "")))
            elif ls_2[i] == "Basic Average Shares":
                for j in range(1, 3):
                    ave_shares.append(int(ls_2[i + j].replace(",", "")))
        profit_rate = np.mean(net_income) / np.mean(total_revenue)
        ROE = np.mean(ave_shares) / np.mean(stockholder_income)

        CACHE_DICT_1[symbol] = {"debt_rate": debt_rate, "profit_rate": profit_rate, "ROE": ROE}
        save_cache(CACHE_DICT_1, CACHE_FILENAME_1)

    return StockInfo(CACHE_DICT_1[symbol]["debt_rate"], CACHE_DICT_1[symbol]["ROE"], CACHE_DICT_1[symbol]["profit_rate"])



if __name__ == "__main__":
    dict = build_symbol_dict()
    symbol = input("Please input a symbol:")
    stock = get_financial_info(symbol, dict)

    if stock.info() is True:
        print("good")
    else:
        print("bad")

