"""
By nature of how crawl_schedule_pages.py works, there will be two copies of
each game that happened in a season; one in the home team's folder,
one in the away team's folder.

This script will create a singular game representation in MongoDB
for all the games in a given season

Usage:
    store_csv_info_to_db.py (--season=<sn>)
"""
import os
from pymongo import MongoClient
from datetime import datetime
from docopt import docopt

from Services.constants import PATH_TO_DATA
from Services.services import convert_csv_to_list, get_teams_for_given_season


def get_info_from_game(season, city, csv):
    game_data = {}
    game_data['away_team_info'] = {}
    game_data['home_team_info'] = {}

    csv_path = os.path.join(PATH_TO_DATA, season, city, 'Csvs', csv)

    list_of_game_rows = convert_csv_to_list(csv_path)

    away_city = list_of_game_rows[0][5]
    home_city = list_of_game_rows[0][6]

    game_data['last_updated'] = datetime.today()
    game_data['away_team_info']['city'] = away_city
    game_data['home_team_info']['city'] = home_city
    game_data['list_of_game_rows'] = list_of_game_rows
    game_data['game_id'] = csv + '_' + away_city + '_' + home_city

    return game_data


def run_storage_of_games_on_season(season, list_of_cities):
    client = MongoClient()
    season_db = client['CFL_'+season]
    games_collection = season_db['games']

    for city in list_of_cities:
        print 'Storing games for {0}'.format(city)
        path_to_csvs = os.path.join(
            PATH_TO_DATA, season, city, 'Csvs'
        )
        all_csvs = [f for f in os.listdir(path_to_csvs) if f.endswith('.csv')]
        for csv in all_csvs:
            game_data = get_info_from_game(season, city, csv)
            saved_game = games_collection.find_one(
                {'list_of_game_rows': game_data['list_of_game_rows']}
            )
            if not saved_game:
                games_collection.insert(game_data)


if __name__ == '__main__':
    args = docopt(__doc__)
    season = args['--season']
    cities = get_teams_for_given_season(season)

    run_storage_of_games_on_season(season, cities)
