"""
This script will:
1) Make the necessary directories for the season
OR
2) Get the schedule pages for each team in a season, which contains the links to each game
OR
3) Get the play-by-play for each game for each team in a season, from the schedule pages

For any given season, (using 2013 as an example)
- first run 1): PYTHONPATH=. python crawl_schedule_pages.py --season=2013 --mkdirs
- then run 2): PYTHONPATH=. python crawl_schedule_pages.py --season=2013 --get_schedules
- lastly run 3): PYTHONPATH=. python crawl_schedule_pages.py --season=2013 --get_pbps

Usage:
    crawl_schedule_pages.py (--season=<sn>) (--mkdirs|--get_schedules|--get_pbps)
"""
import os
import time
from bs4 import BeautifulSoup
from docopt import docopt
from subprocess import call
from Services.constants import PATH_TO_DATA, BASE_CFL_URL
from Services.services import get_teams_for_given_season, write_to_csv
from Services.pbp_scraper_for_game import get_game_rows_from_url


def create_data_dirs(season):
    """
    Onetime usage to create team directories for season
    """
    list_of_cities = get_teams_for_given_season(season)
    SAVED_PATH = os.path.join(PATH_TO_DATA, season)

    for city in list_of_cities:
        path_to_city_dir = os.path.join(SAVED_PATH, city)
        os.mkdir(path_to_city_dir)
        path_to_pbp_source_dir = os.path.join(SAVED_PATH, city, 'PlayByPlay')
        os.mkdir(path_to_pbp_source_dir)
        path_to_pbp_csvs_dir = os.path.join(SAVED_PATH, city, 'Csvs')
        os.mkdir(path_to_pbp_csvs_dir)


def get_schedule_pages_map(season):
    if season not in ('2013', '2014'):
        raise Exception('No play-by-play before 2013, 2014')
    # Before 2013, no play by play for games AFAIK
    BC_SCHEDULE_PAGE = '{0}/schedule/year/{1}/1'.format(BASE_CFL_URL, season)
    CAL_SCHEDULE_PAGE = '{0}/schedule/year/{1}/2'.format(BASE_CFL_URL, season)
    EDM_SCHEDULE_PAGE = '{0}/schedule/year/{1}/3'.format(BASE_CFL_URL, season)
    SAS_SCHEDULE_PAGE = '{0}/schedule/year/{1}/4'.format(BASE_CFL_URL, season)
    WIN_SCHEDULE_PAGE = '{0}/schedule/year/{1}/5'.format(BASE_CFL_URL, season)
    HAM_SCHEDULE_PAGE = '{0}/schedule/year/{1}/6'.format(BASE_CFL_URL, season)
    TOR_SCHEDULE_PAGE = '{0}/schedule/year/{1}/7'.format(BASE_CFL_URL, season)
    # Ottawa's 2013 page doesn't exist
    OTT_SCHEDULE_PAGE = '{0}/schedule/year/{1}/65'.format(BASE_CFL_URL, season)
    MTL_SCHEDULE_PAGE = '{0}/schedule/year/{1}/9'.format(BASE_CFL_URL, season)
    SCHEDULE_PAGES_MAP = {
        'BC': BC_SCHEDULE_PAGE,
        'Calgary': CAL_SCHEDULE_PAGE,
        'Edmonton': EDM_SCHEDULE_PAGE,
        'Saskatchewan': SAS_SCHEDULE_PAGE,
        'Winnipeg': WIN_SCHEDULE_PAGE,
        'Hamilton': HAM_SCHEDULE_PAGE,
        'Toronto': TOR_SCHEDULE_PAGE,
        'Ottawa': OTT_SCHEDULE_PAGE,
        'Montreal': MTL_SCHEDULE_PAGE
    }

    schedule_pages_map = SCHEDULE_PAGES_MAP.copy()
    if season == '2013':
        schedule_pages_map.pop('Ottawa', None)

    return schedule_pages_map


def collect_schedule_pages_for_teams(season):
    schedule_pages_map = get_schedule_pages_map(season)
    SAVED_PATH = os.path.join(PATH_TO_DATA, season)

    for city, url in schedule_pages_map.iteritems():
        path_to_city_dir = os.path.join(SAVED_PATH, city)
        name_of_file = os.path.join(path_to_city_dir, 'schedule.html')
        print 'URL {0}'.format(url)
        call(['curl', '-o', name_of_file, url])
        time.sleep(10)

    return True


def get_game_urls_from_schedule_page(path_to_schedule_page):
    game_urls = []

    soup = BeautifulSoup(open(path_to_schedule_page))
    schedule_table = soup.find('div', class_='sked_tbl')
    # The first row is a header row, and every 2nd row is just
    # a line break for the table for visual spacing
    rows = schedule_table.find_all('tr')[1::2]
    for row in rows:
        cells = row.find_all('td')
        cell_with_url = cells[9]
        href = cell_with_url.a['href']
        complete_url = BASE_CFL_URL + href
        game_urls.append(complete_url)

    return game_urls


def collect_pbps_for_teams(season):
    list_of_cities = get_teams_for_given_season(season)
    SAVED_PATH = os.path.join(PATH_TO_DATA, season)
    print 'Beginning play by play collection for {0}'.format(season)

    for city in list_of_cities:
        print '{0}\n--------'.format(city)
        path_to_city_dir = os.path.join(SAVED_PATH, city)
        path_to_schedule_page = os.path.join(path_to_city_dir, 'schedule.html')
        all_game_urls = get_game_urls_from_schedule_page(path_to_schedule_page)
        for i, url in enumerate(all_game_urls):
            # Adjust the counter, I want my games starting at 01 not 00
            i += 1
            name = str(i)
            if len(name) == 1:
                name = '0'+name
            path_to_pbp_source = os.path.join(
                path_to_city_dir, 'PlayByPlay', name+'.html'
            )
            path_to_pbp_csv = os.path.join(
                path_to_city_dir, 'Csvs', name+'.csv'
            )
            game_rows = get_game_rows_from_url(
                url, save_to_dest=path_to_pbp_source
            )
            write_to_csv(game_rows, path_to_pbp_csv)


if __name__ == '__main__':
    args = docopt(__doc__)
    season = args['--season']
    mkdirs = args['--mkdirs']
    get_schedules = args['--get_schedules']
    get_pbps = args['--get_pbps']

    if mkdirs:
        create_data_dirs(season=season)
    elif get_schedules:
        collect_schedule_pages_for_teams(season=season)
    elif get_pbps:
        collect_pbps_for_teams(season)
