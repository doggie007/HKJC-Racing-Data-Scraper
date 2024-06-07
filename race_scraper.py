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

DEBUG = True


class RaceScraper:
    def __init__(self, start_date : datetime.datetime, end_date : datetime.datetime, race_info_folder_path : str, race_result_folder_path : str):
        self.base_url = "https://racing.hkjc.com/racing/information/english/Racing/LocalResults.aspx"
        self.successful_scrapes = 0 # A successful scrape is 1 successful race result scraped 
        self.start_date = start_date
        self.end_date = end_date
        self.info_path = race_info_folder_path
        self.result_path = race_result_folder_path

    def parse_race_info(self, soup : BeautifulSoup) -> Optional[pd.DataFrame]:
        table = soup.find('table', style="width: 760px;")

        if not table:
            if DEBUG: print("No race info found")
            return None


        info = soup.find('span', class_="f_fl f_fs13").text.split()

        date = info[2]
        location = "HV" if info[3] == "Happy" else "SH"

        table_body = table.find('tbody')
        table_body_data = table_body.find_all("td")

        class_and_dist = list(map(str.strip, table_body_data[3].text.split('-')))

        
        # Check if weird race 
        if not ("Class" in class_and_dist[0]):
            if DEBUG: print("Strange race so ignore")
            return None
        race_class = class_and_dist[0]
        race_dist = class_and_dist[1]

        going = table_body_data[5].text
        course = table_body_data[8].text


        dict_ = {
            "Date": date,
            "Location": location,
            "Class": race_class,
            "Distance": race_dist,
            "Going": going,
            "Course": course
        }

        df = pd.DataFrame([dict_])
        return df
    
    def parse_race_results(self, soup : BeautifulSoup) -> Optional[pd.DataFrame]:
        table = soup.find('table', class_="f_tac table_bd draggable")
        if not table: 
            if DEBUG: print("No race results found")
            return None
        
        table_df = pd.read_html(StringIO(str(table)))[0]

        # Add horse urls after horse name column
        horse_urls = []
        data = table.find('tbody')
        rows = data.find_all('tr')
        for row in rows:
            items = row.find_all('td')
            horse_url = items[2].find("a").get('href')
            horse_urls.append(horse_url)
        
        table_df.insert(3, "Horse URL", horse_urls, True)

        return table_df


    def scrape_specific(self, date : datetime.datetime, race_num : int) -> bool:
        stringed_date = date.strftime('%Y/%m/%d')
        params = {
            "RaceDate": stringed_date,
            "RaceNo": race_num
        }

        try:
            r = requests.get(self.base_url, params=params, timeout=10)

            if DEBUG: print(f"Request url is {r.url}")

            # If redirected to overseas return false
            if "overseas" in r.url:
                if DEBUG: print("Redirected to overseas so no information")
                return False

            # Raise if any request error occurred
            r.raise_for_status()

            # Parse response
            soup = BeautifulSoup(r.content, 'html.parser')

            # Ensure that there is valid information
            soup_text = soup.get_text()
            if "No information" in soup_text or "Information will be released shortly" in soup_text:
                if DEBUG: print("No information found")
                return False
        # Handle request errors
        except HTTPError as http_err:
            if DEBUG: print(f'HTTP error occurred: {http_err}')  # e.g. 404 Not Found
            return False
        except Timeout as timeout_err:
            if DEBUG: print(f'Timeout error occurred: {timeout_err}')  # e.g. request timed out
            return False
        except RequestException as req_err:
            if DEBUG: print(f'Request error occurred: {req_err}')  # e.g. network issues, invalid URL
            return False

        parsed_race_info = self.parse_race_info(soup)
        if parsed_race_info is None: return False

        parsed_race_results = self.parse_race_results(soup)
        if parsed_race_results is None: return False

        # Write to folder
        path_friendly_date = date.strftime('%Y-%m-%d')

        parsed_race_info.to_csv(os.path.join(self.info_path,  f"{path_friendly_date}_{race_num}_info.csv"), index = False)
        parsed_race_results.to_csv(os.path.join(self.result_path,  f"{path_friendly_date}_{race_num}_result.csv"), index = False)

        return True

    def scrape(self):
        current_date = self.start_date
        tried = 0
        start_time = time.time()
        while current_date <= self.end_date:
            num_failed = 0
            for race_num in range(1,13):
                print(f"Attempt - date: {current_date.strftime('%Y/%m/%d')} num: {race_num}")
                tried += 1
                success = self.scrape_specific(current_date, race_num)
            
                if not success: 
                    print(f"Failed")
            
                    num_failed += 1
                    if num_failed > 2:
                        print(f"Stopped scraping for {current_date.strftime('%Y/%m/%d')}")
                        break
                else:
                    print(f"Success")
                    self.successful_scrapes += 1
            current_date += datetime.timedelta(days=1)
        
        print("")
        time_taken = time.time() - start_time
        print(f"Successfully scraped {self.successful_scrapes}; Total attempted {tried}; Time taken {time_taken}s; Seconds per scrape {time_taken / tried}")


