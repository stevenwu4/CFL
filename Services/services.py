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
    """
    Input:
    0. path_to_csv: 

    Description:
    - This function reads the file and returns a list of lists,
    each inner list having 4 indices for Time, Away, Score, Home

    Returns: list
    0. list_of_game_rows: the list of game rows
    """
    with open(path_to_csv, 'rU') as f:
        reader = csv.reader(f)
        list_of_game_rows = [row for row in reader]

    return list_of_game_rows
