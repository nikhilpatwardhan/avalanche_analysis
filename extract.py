from bs4 import BeautifulSoup
import pandas as pd
import requests as r
import logging

BASE_URL = 'https://utahavalanchecenter.org'
AVALANCHES_URL_SUFFIX = '/avalanches/fatalities'

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0'}


def get_overview_data():
    """
    Scrapes the overview page
    :return: list of dicts
    """
    req = r.get(BASE_URL + AVALANCHES_URL_SUFFIX, headers=HEADERS)
    data = req.text
    soup = BeautifulSoup(data, features="html.parser")

    content = soup.findAll('div', {'class': 'view-content'})[0]
    trs = content.find_all('tr')
    res = []

    for tr in trs:
        tds = tr.find_all('td')
        if not tds:
            continue

        res_dict = _parse_overview_tds(tds)
        if res_dict:
            res.append(res_dict)

    return res


def _parse_overview_tds(tds):
    res_dict = {}
    for td in tds:
        tags = td.get('class')
        prefix = 'views-field-field-'
        for tag in tags:
            if tag.startswith(prefix):
                res_dict[tag[len(prefix):]] = ''.join(td.stripped_strings)
            elif tag == 'views-field-title':
                res_dict['url'] = td.a['href']
    return res_dict


def get_avalanche_detail(ov_dict):
    """
    Scrapes the avalanche details page and adds keys into the overview dictionary
    :param ov_dict: single row (dict) from overview data
    :return: dict
    """
    req = r.get(BASE_URL + ov_dict['url'], headers=HEADERS)
    data = req.text
    soup = BeautifulSoup(data, features='html.parser')
    content = soup.findAll('div', {'class': 'page-content'})[0]
    divs = content.find_all('div')

    key = ''
    for i, div in enumerate(divs):
        if div.text == 'Accident and Rescue Summary':
            break

        if i % 2 == 0:
            key = div.text
        else:
            ov_dict[key] = div.text

    return ov_dict


if __name__ == '__main__':
    ov_data = get_overview_data()
    res = []
    for ov_dict in ov_data:
        res.append(get_avalanche_detail(ov_dict))
    df = pd.DataFrame(res)
    df.to_csv("avalanche_data.csv")