import os
import sys
import argparse
import logging
import pandas as pd
from make_features import make_game_features
from make_features import make_team_features
sys.path.append('auxiliary')  # noqa: E402
from io_json import read_json
from argparser_types import is_valid_parent_path

logging.basicConfig(level=logging.INFO)


def main(season, results_file, standings_file, f4_file):
    '''
    Extract features (game and team) from the fetched data from the
    Euroleague's site
    '''

    settings = read_json('settings/feature_extraction.json')
    feature_dir = settings['feature_dir']
    match_level_file_ = settings['match_level_feature_file_prefix']
    team_level_file_ = settings['team_level_feature_file_prefix']
    match_level_file = os.path.join(
        feature_dir, '%s_%d_%d.csv' % (match_level_file_, season - 1, season))
    team_level_file = os.path.join(
        feature_dir, '%s_%d_%d.csv' % (team_level_file_, season - 1, season))

    data = pd.read_csv(results_file)
    standings = pd.read_csv(standings_file)
    f4teams = read_json(f4_file)

    # Specify the F4 teams of the *previous* year
    f4Teams = f4teams[str(season - 1)]

    # make game features
    feats = make_game_features(data, standings, f4Teams)

    # save features to file.
    logging.info('save match-level features')
    feats.to_csv(match_level_file, index=False)

    # make team features
    team_feats = make_team_features(data, standings, f4Teams)
    # save features to file
    logging.info('save team-level features')
    team_feats.to_csv(team_level_file, index=False)
    return


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--season', required=True, type=int,
                        help="the ending year of the season")
    parser.add_argument('-r', '--results', required=True,
                        type=lambda x: is_valid_parent_path(parser, x),
                        help="results file of a season")
    parser.add_argument('-t', '--table', required=True,
                        type=lambda x: is_valid_parent_path(parser, x),
                        help="table/standings file of a season")
    parser.add_argument('-f', '--final_four', required=True,
                        type=lambda x: is_valid_parent_path(parser, x),
                        help="final four file of teams of previous a season")
    args = parser.parse_args()

    main(args.season, args.results, args.table, args.final_four)
