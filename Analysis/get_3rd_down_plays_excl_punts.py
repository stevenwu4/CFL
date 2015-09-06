"""
Simple script that will read in your MongoDB game data,
find all 3rd down plays that didn't end in a punt,
and write it to a .csv file for further analysis

Usage:
    get_3rd_down_plays_excl_punts.py (--season=<sn>)
"""

import csv
from pymongo import MongoClient
from docopt import docopt

DOWN_INDEX = 1
TYPE_INDEX = 2


def write_3rd_down_plays_excl_punts_for_season(season):
    client = MongoClient()
    season_db = client['CFL_'+season]
    games_collection = season_db['games']

    filename = '{0}_3rd_down_plays_excl_punts.csv'.format(season)
    with open(filename, 'w') as f:
        writer = csv.writer(f)
        for game in games_collection.find():
            for row in game['list_of_game_rows']:
                down = row[DOWN_INDEX].strip()
                play_type = row[TYPE_INDEX].strip()
                if down == '3' and play_type != 'Punt':
                    writer.writerow(row)
    print 'Done creating {0}'.format(filename)


if __name__ == '__main__':
    args = docopt(__doc__)
    season = args['--season']

    write_3rd_down_plays_excl_punts_for_season(season=season)
