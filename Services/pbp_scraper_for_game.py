"""
This file is used as a module for our programs in Tasks, but can be used
from the cmd line to get the csv for a given URL as well

eg: PYTHONPATH=. python pbp_scraper_for_game.py
--url=http://www.cfl.ca/statistics/statsGame/id/11805
--filename=blah.csv

Usage:
    pbp_scraper_for_game.py (--url=<u>) (--filename=<fn>)
"""

import time
from docopt import docopt
from bs4 import BeautifulSoup
from selenium import webdriver

from Services.constants import PLAYBYPLAY_BTN_XPATH
from Services.services import write_to_csv


def get_game_rows_from_url(url, save_to_dest=None):
    """
    Parses the page using a selenium driver instance
    to click the play by play button.

    Returns the list of game rows
    """
    driver = webdriver.Firefox()
    driver.get(url)
    # No issues with the DOM; slow down the time between crawls
    time.sleep(10)
    playbyplay_btn = driver.find_element_by_xpath(PLAYBYPLAY_BTN_XPATH)
    playbyplay_btn.click()
    soup = BeautifulSoup(driver.page_source)
    if save_to_dest:
        f = open(save_to_dest, 'w')
        f.write(driver.page_source.encode('utf-8'))
        f.close()
    # Get away/home teams
    away_div = soup.find('div', id='awayteam')
    away_team = away_div.find('h3', class_='cityname').text
    home_div = soup.find('div', id='hometeam')
    home_team = home_div.find('h3', class_='cityname').text

    # Get game rows
    pbp_div = soup.find('div', id='stat-game-pbp')
    pbp_inner_div = pbp_div.find('div', id='pbp-stats')
    pbp_table = pbp_inner_div.find('table', id='pbp-table')
    rows = pbp_table.find_all('tr')

    all_times = []
    all_downs = []
    all_types = []
    all_yards = []
    all_details = []
    all_aways = []
    all_homes = []

    for row in rows:
        # The rows we care about don't have <th></th>
        if row.th:
            continue
        cells = row.find_all('td')
        all_times.append(cells[2].text.strip().encode())
        all_downs.append(cells[3].text.strip().encode())
        all_types.append(cells[4].text.strip().encode())
        all_yards.append(cells[5].text.strip().encode())
        all_details.append(cells[6].text.strip().encode())
        all_aways.append(cells[7].text.strip().encode())
        all_homes.append(cells[8].text.strip().encode())

    header_row = [
        'Time', 'Down', 'Type', 'Yards',
        'Details', away_team, home_team
    ]
    list_of_game_rows = [header_row]

    for t, down, types, yards, details, away, home in zip(
        all_times, all_downs, all_types, all_yards,
        all_details, all_aways, all_homes
    ):
        new_row = []
        new_row.append(t)
        new_row.append(down)
        new_row.append(types)
        new_row.append(yards)
        new_row.append(details)
        new_row.append(away)
        new_row.append(home)
        list_of_game_rows.append(new_row)

    driver.close()

    return list_of_game_rows


if __name__ == '__main__':
    args = docopt(__doc__)
    url = args['--url']
    filename = args['--filename']

    game_rows = get_game_rows_from_url(url)
    write_to_csv(game_rows, filename)
