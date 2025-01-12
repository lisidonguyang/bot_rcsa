import os
from selenium import webdriver
from selenium.webdriver import FirefoxOptions
import time
from bs4 import BeautifulSoup
import re
import pandas as pd



def web_scraper() -> pd.DataFrame:
    ff_options = FirefoxOptions()
    ff_options.add_argument('--no-sandbox')
    ff_options.add_argument('--disable-dev-shm-usage')
    ff_options.add_argument('--headless')
    
    driver = webdriver.Remote(command_executor=f"http://51.75.17.83:4444/wd/hub", options=ff_options)
        # this is just to ensure that the page is loaded
    time.sleep(5)

    html = driver.page_source

        # this renders the JS code and stores all
        # of the information in static HTML code.

        # Application de Beautiful Soup
    soup = BeautifulSoup(html, "html.parser")

    driver.close()

    # find href with target self
    matchs = soup.find_all(href=re.compile("match-"))
    nb_match = len(matchs)

    df = pd.DataFrame(columns=['home', 'away'])
    team_names = []
    for match in matchs:
        href = match.get('href', '')
        # Extract team name from href
        team_match = re.search(r'/fr/catalogue/match-([^"]+)', href)
        if team_match:
            team_names.append(team_match.group(1))

    # Print results
    print(f"Number of matches: {nb_match}")
    print("Team names:")
    for name in team_names:
        name = name.replace('-', ' ')
        print(name)
        
        if name.startswith('rcsa'):
            df = df.append({'home': 'rcsa', 'away': name.replace('rcsa', '')}, ignore_index=True)
        elif name.endswith('rcsa'):
            df = df.append({'home': name.replace('rcsa', ''), 'away': 'rcsa'}, ignore_index=True)
                
    return df


