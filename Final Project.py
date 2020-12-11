#################################
##### Name:     Ziyu Wang
##### Uniqname: ziwa
#################################

from bs4 import BeautifulSoup
import requests
import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

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
        if (np.mean(self.debt_rate) < 0.4) & (np.mean(self.ROE) > 15) & (np.mean(self.profit_rate) > 0.1):
            print("This stock is worth holding")
            return True
        else:
            print("Be cautious with this stock, Because:")
            if np.mean(self.debt_rate) >= 0.4:
                print("Debt rate is too high")
            if np.mean(self.ROE) <= 15:
                print("ROE is too low")
            if np.mean(self.profit_rate) <= 0.1:
                print("Profit rate is too low")
            return False

    def plot(self):
        year_list = [2020, 2019, 2018, 2017]
        x_major_locator = plt.MultipleLocator(1)

        def to_percent(temp, position):
            return '%1.0f' % (100 * temp) + '%'

        if 0 in self.debt_rate:
            self.debt_rate.remove(0)
        for i in range(len(self.debt_rate), 4):
            self.debt_rate.append(None)
        plt.scatter(year_list, self.debt_rate, c="blue")
        plt.plot(year_list, self.debt_rate, c="blue")
        plt.title("Debt Rate", fontsize=24)
        plt.tick_params(axis="both", which="major", labelsize=14)
        plt.xlim(2016.8, 2020.2)
        plt.xlabel("Year", fontsize=18)
        plt.ylabel("Debt Rate", fontsize=18)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))
        plt.show()

        if 0 in self.ROE:
            self.ROE.remove(0)
        print(self.ROE)
        for i in range(len(self.ROE), 4):
            self.ROE.append(None)
        print(self.ROE)
        plt.scatter(year_list, self.ROE, c="red")
        plt.plot(year_list, self.ROE, c="red")
        plt.title("ROE", fontsize=24)
        plt.tick_params(axis="both", which="major", labelsize=14)
        plt.xlim(2016.8, 2020.2)
        plt.xlabel("Year", fontsize=18)
        plt.ylabel("ROE", fontsize=18)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        plt.show()

        if 0 in self.profit_rate:
            self.profit_rate.remove(0)
        print(self.profit_rate)
        for i in range(len(self.profit_rate), 4):
            self.profit_rate.append(None)
        print(self.profit_rate)
        plt.scatter(year_list, self.profit_rate, c="green")
        plt.plot(year_list, self.profit_rate, c="green")
        plt.title("Profit Rate", fontsize=24)
        plt.tick_params(axis="both", which="major", labelsize=14)
        plt.xlim(2016.8, 2020.2)
        plt.xlabel("Year", fontsize=18)
        plt.ylabel("Profit Rate", fontsize=18)
        ax = plt.gca()
        ax.xaxis.set_major_locator(x_major_locator)
        ax.yaxis.set_major_formatter(ticker.FuncFormatter(to_percent))
        plt.show()


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
    total_num = int(total_num[num_begin + 3: num_end - 1])

    # Add symbols and link to income statement url
    loop_num = int(total_num / 25) + 1
    for i in range(loop_num):
        resp_1 = requests.get(find_symbol_url + str(i * 25))
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
        print("Fetching")
        resp_1 = requests.get(symbol_dict[symbol]["balance_sheet"])
        soup_1 = BeautifulSoup(resp_1.text, "html.parser")

        ls_1 = []
        total_assets = []
        total_debt = []
        debt_rate = []
        cash_row = soup_1.find_all(class_="D(tbr) fi-row Bgc($hoverBgColor):h")
        for i in cash_row:
            a = i.find_all("span")
            for b in a:
                ls_1.append(b.get_text())

        for i in range(len(ls_1)):
            if ls_1[i] == "Total Assets":
                for j in range(1, 5):
                    if ls_1[i + j].replace(",", "").replace("-", "").isnumeric() is True:
                        total_assets.append(float(ls_1[i + j].replace(",", "")))
                    else:
                        total_assets.append(None)
            elif ls_1[i] == "Total Debt":
                for j in range(1, 5):
                    if ls_1[i + j].replace(",", "").replace("-", "").isnumeric() is True:
                        total_debt.append(float(ls_1[i + j].replace(",", "")))
                    else:
                        total_assets.append(None)

        for i in range(min(len(total_debt), len(total_assets))):
            if total_debt[i] is not None and total_debt[i] != 0 \
                    and total_assets[i] is not None and total_assets[i] != 0:
                debt_rate.append(total_debt[i] / total_assets[i])
            else:
                break

        resp_2 = requests.get(symbol_dict[symbol]["income_statement"])
        soup_2 = BeautifulSoup(resp_2.text, "html.parser")

        ls_2 = []
        total_revenue = []
        net_income = []
        stockholder_income = []
        ave_shares = []
        profit_rate = []
        ROE = []
        income = soup_2.find_all(class_="D(tbr) fi-row Bgc($hoverBgColor):h")
        for i in income:
            a = i.find_all("span")
            for b in a:
                ls_2.append(b.get_text())

        for i in range(len(ls_2)):
            if ls_2[i] == "Total Revenue":
                for j in range(2, 6):
                    if ls_2[i + j].replace(",", "").replace("-", "").isnumeric() is True:
                        total_revenue.append(float(ls_2[i + j].replace(",", "")))
                    else:
                        total_revenue.append(None)
            elif ls_2[i] == "Net Income from Continuing & Discontinued Operation":
                for j in range(2, 6):
                    if ls_2[i + j].replace(",", "").replace("-", "").isnumeric() is True:
                        net_income.append(float(ls_2[i + j].replace(",", "")))
                    else:
                        net_income.append(None)
            elif ls_2[i] == "Net Income Common Stockholders":
                for j in range(2, 6):
                    if ls_2[i + j].replace(",", "").replace("-", "").isnumeric() is True:
                        stockholder_income.append(float(ls_2[i + j].replace(",", "")))
                    else:
                        stockholder_income.append(None)
            elif ls_2[i] == "Basic Average Shares":
                for j in range(1, 5):
                    if ls_2[i + j].replace(",", "").replace("-", "").isnumeric() is True:
                        ave_shares.append(float(ls_2[i + j].replace(",", "")))
                    else:
                        ave_shares.append(None)

        for i in range(min(len(net_income), len(total_revenue))):
            if net_income[i] is not None and net_income[i] != 0 \
                    and total_revenue[i] is not None and total_revenue[i] != 0:
                profit_rate.append(net_income[i] / total_revenue[i])
            else:
                break


        for i in range(min(len(stockholder_income), len(ave_shares))):
            if stockholder_income[i] is not None and stockholder_income[i] != 0 \
                    and ave_shares[i] is not None and ave_shares[i] != 0:
                ROE.append(stockholder_income[i] / ave_shares[i])
            else:
                break

        CACHE_DICT_1[symbol] = {"debt_rate": debt_rate, "profit_rate": profit_rate, "ROE": ROE}
        save_cache(CACHE_DICT_1, CACHE_FILENAME_1)

    return StockInfo(CACHE_DICT_1[symbol]["debt_rate"], CACHE_DICT_1[symbol]["ROE"],
                     CACHE_DICT_1[symbol]["profit_rate"])


if __name__ == "__main__":
    dict = build_symbol_dict()
    print("Show first 10 symbols")
    for i in range(10):
        print(str(i + 1) + ". " + list(dict.keys())[i])
    symbol = input("Please input a symbol:")
    # symbol = "AAPL"
    stock = get_financial_info(symbol, dict)

    stock.info()
    stock.plot()
