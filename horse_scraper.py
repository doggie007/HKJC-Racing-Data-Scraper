import requests
from requests.exceptions import HTTPError, Timeout, RequestException
from bs4 import BeautifulSoup
import pandas as pd
import datetime
from urllib.parse import urlencode
from io import StringIO
from typing import Optional
import os
import time

folder_path = 'Data/Race-Result'

files = sorted(os.listdir(folder_path))[:10]

base_url = "https://racing.hkjc.com"


def parse(soup):
    soup = BeautifulSoup(r.content, 'html.parser')
    table = soup.find('table', class_="table_eng_text")
    if not table:
        return None
    # print(pd.read_html(StringIO(str(table)))[0])
    rows = table.find_all('tr')
    rows = list(map(lambda x: x.find_all('td'), rows))
    country_of_origin, age = rows[0][2].text.split(" / ")
    colour, sex = rows[1][2].text.split(" / ")[-2:]
    print(country_of_origin, age, colour, sex)

for file_name in files:
    file_path = os.path.join(folder_path, file_name)
    df = pd.read_csv(file_path)

    for url in df["Horse URL"]:
        r = requests.get(base_url + url)
        soup = BeautifulSoup(r.content, 'html.parser')
        print(parse(soup))
        break
    break


        
