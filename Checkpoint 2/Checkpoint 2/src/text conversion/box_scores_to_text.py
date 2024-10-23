import pandas as pd
import os
import re
import math

BOX_SCORE_DIRECTORY = "./box scores/"
CONVERTED_TEXT_DIRECTORY = "./converted text/"


def get_qb_highlights(offense_df):
    qb_highlight_string = ""  # String to capture QB highlights
    # Only focus on QBs that played significantly during the game
    qb_passing = offense_df[offense_df['Passing_Att'] > 10]
    for row in qb_passing.iterrows():
        qb_row = row[1]
        qb_summary = f'{qb_row["Player"]} was {qb_row["Passing_Cmp"]} of {qb_row["Passing_Att"]} for {qb_row["Passing_Yds"]} yards, {qb_row["Passing_TD"]} touchdowns and {qb_row["Passing_Int"]} interceptions. '
        # Include summary for each Quarterback
        qb_highlight_string += qb_summary
    return qb_highlight_string


def get_rec_yds_highlights(offense_df):
    rec_yds_highlight_string = ""  # String to capture Receiving Yard highlights
    rec_yds_highlights = offense_df[offense_df['Receiving_Yds'] > 100]
    for row in rec_yds_highlights.iterrows():
        rec_row = row[1]
        rec_summary = f'{rec_row["Player"]} had {rec_row["Receiving_Yds"]} receiving yards. '
        # Include summary for each receiving statistic
        rec_yds_highlight_string += rec_summary
    return rec_yds_highlight_string


def get_scoring_highlights(scoring_df):
    # String to capture Scoring highlights
    scoring_highlight_string = ""
    # Get team names
    teams = scoring_df.columns[-2:]
    scoring_per_quarter = {}
    cumulative_score = {}
    start_q4_scores = []
    scores = scoring_df[teams]
    # For each team, calculate each of their scoring streaks and determine if any are highlight worthy
    for team in teams:
        other_team = list(filter(lambda x: x != team, teams))[0]
        team_scoring_streaks = scores.groupby([other_team])[team].apply(list)
        for streak in team_scoring_streaks:
            total_streak_points = streak[-1] - streak[0]
            if total_streak_points > 16:
                # Add highlight worthy streaks to the string
                scoring_highlight_string += f'{team} scored {total_streak_points} unanswered points during the game. '
        # Initialize scoring trackers
        scoring_per_quarter[team] = [0] * 4
        cumulative_score[team] = [0] * 4
    previous_row = None
    for row in scoring_df.iterrows():
        scoring_row = row[1]
        quarter = scoring_row["Quarter"]
        # If there is overtime, include it in the highlights
        if quarter == "OT":
            scoring_highlight_string += f'{previous_row["Tm"]} {previous_row["Detail"]} to force the game into overtime. '
            continue
        quarter = float(scoring_row["Quarter"])
        if not math.isnan(quarter) and quarter > 1:
            quarter = int(quarter)
            for team in teams:
                # Calculate and store first quarter scoring data
                if quarter == 2 and previous_row is not None:
                    scoring_per_quarter[team][0] = previous_row[team]
                    cumulative_score[team][0] = previous_row[team]

                # Calculate and store second and third quarter scoring data
                elif previous_row is not None:
                    cumulative_score[team][quarter - 2] = previous_row[team]
                    scoring_per_quarter[team][quarter - 2] = previous_row[team] - \
                        cumulative_score[team][quarter - 3]
        previous_row = scoring_row

        # Calculate and store foruth quarter scoring data
        for team in teams:
            cumulative_score[team][3] = previous_row[team]
            scoring_per_quarter[team][3] = previous_row[team] - \
                cumulative_score[team][2]
    team_final_scores = []
    # Calculate final scores, as well as the scores at the start of the fourth quarter.
    for team in teams:
        start_q4_scores.append([team, cumulative_score[team][2]])
        start_q4_scores = sorted(
            start_q4_scores, key=lambda x: x[1], reverse=True)
        team_final_score = scoring_df.iloc[-1][team]
        team_final_scores.append([team, team_final_score])
        team_final_scores = sorted(
            team_final_scores, key=lambda x: x[1], reverse=True)
        first_half_sum = sum(scoring_per_quarter[team][:2])
        second_half_sum = sum(scoring_per_quarter[team][2:])
        # If a team scored at least 27 points in a quarter, add it as a highlight
        if first_half_sum >= 27:
            scoring_highlight_string += f'{team} scored {first_half_sum} points in the first half. '
        if second_half_sum >= 27:
            scoring_highlight_string += f'{team} scored {second_half_sum} points in the second half. '
    # Determine if there was a comeback and add it as a highlight
    q4_deficit = start_q4_scores[0][1] - start_q4_scores[1][1]
    if q4_deficit >= 14 and team_final_scores[0][0] == start_q4_scores[1][0]:
        scoring_highlight_string += f'{team_final_scores[0][0]} came back from a {q4_deficit} point deficit in the 4th quarter. '
    # Include the final score
    scoring_highlight_string += f'{team_final_scores[0][0]} defeated {team_final_scores[1][0]} with a final score of {team_final_scores[0][1]}-{team_final_scores[1][1]}'
    return scoring_highlight_string


def get_td_highlights(offense_df):
    td_highlight_string = ""  # String to capture Touchdown Statistic highlights
    td_highlights = offense_df[offense_df['Rushing_TD'] +
                               offense_df['Receiving_TD'] > 1]
    for row in td_highlights.iterrows():
        td_row = row[1]
        # If a player scored more than 1 touchdown, add it to the highlights
        td_summary = f'{td_row["Player"]} had {td_row["Receiving_TD"]} receiving touchdowns and {td_row["Rushing_TD"]} rushing touchdowns. '
        td_highlight_string += td_summary
    return td_highlight_string


def get_big_plays(pbp_df):
    big_play_string = ""  # String to capture big plays
    for row in pbp_df.iterrows():
        play_row = row[1]
        play = play_row["Detail"]
        if type(play) is not float:
            # Extract the yards gained on the play
            yards_gained = re.search(r'(?<!punts\s)\bfor \d+\s+yards\b', play)
            if yards_gained or "touchdown" in play:
                # Add the play to the highlights if it resulted in a touchdown, or gained more than 40 yards total.
                if "touchdown" in play:
                    big_play_string += play + ". "
                else:
                    total_yardage = int(yards_gained.group().split(" ")[1])
                    if total_yardage > 40 or total_yardage <= -10:
                        big_play_string += play + ". "
    return big_play_string


def run_diagnostics():
    # Calculate statistics for the generated articles
    num_docs = 0
    original_char_count = 0
    original_word_count = 0
    for game in os.listdir(CONVERTED_TEXT_DIRECTORY):
        with open(f'{CONVERTED_TEXT_DIRECTORY}{game}', 'r', encoding='utf-8') as file:
            num_docs += 1
            for line in file:
                original_char_count += len(line)
                original_word_count += len(line.split(" "))

    print("Number of articles:", num_docs)
    print("Average number of words per converted article",
          original_word_count / num_docs)
    print("Average number of characters per converted article",
          original_char_count / num_docs)
    print("")


# Iterate through the box score directory and generate text files for each of the box scores
for directory in os.listdir(BOX_SCORE_DIRECTORY):
    converted_text_game_path = CONVERTED_TEXT_DIRECTORY + directory + "/"
    box_score_game_path = BOX_SCORE_DIRECTORY + directory + "/"
    print(f'Processing {directory}...')
    offense_df = pd.read_csv(box_score_game_path +
                             "Offense-Statistics-" + directory + ".csv")

    pbp_df = pd.read_csv(box_score_game_path +
                         "Play-By-Play-" + directory + ".csv")

    scoring_df = pd.read_csv(box_score_game_path +
                             "Scoring-Summary-" + directory + ".csv")

    converted_text = get_qb_highlights(
        offense_df) + get_rec_yds_highlights(offense_df) + get_td_highlights(offense_df) + get_big_plays(pbp_df) + get_scoring_highlights(scoring_df)
    with open(f'{CONVERTED_TEXT_DIRECTORY}{directory}.txt', "w") as f:
        f.write(converted_text)

print("Text conversion completed!")
run_diagnostics()
