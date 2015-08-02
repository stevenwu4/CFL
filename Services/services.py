import csv
from Services.constants import TEAMS_2013, TEAMS_2014


def get_teams_for_given_season(season):
    assert isinstance(season, str)
    if season == '2013':
        teams = TEAMS_2013
    elif season == '2014':
        teams = TEAMS_2014
    else:
        raise ValueError('ERROR: Season input not in valid range')

    return teams


def convert_csv_to_list(path_to_csv):
    with open(path_to_csv, 'rU') as f:
        reader = csv.reader(f)
        list_of_game_rows = [row for row in reader]

    return list_of_game_rows


def write_to_csv(list_of_game_rows, name_of_csv):
    with open(name_of_csv, 'wb') as f:
        writer = csv.writer(f)
        for row in list_of_game_rows:
            writer.writerow(row)
    print (
        'csv {0} conversion successful\n'
        'number of rows: {1}'
        .format(name_of_csv, len(list_of_game_rows))
    )
    print '-'*20
