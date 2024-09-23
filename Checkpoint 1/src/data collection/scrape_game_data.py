import os # Directory Creation
from time import sleep # Adhering to rate limiting
from bs4 import BeautifulSoup # HTML scraping library
from selenium import webdriver # For webscraping pro-football-reference, as some elements take time to load
import requests
import pandas as pd
from io import StringIO


YEAR = 2023
WEEKLY_SCHEDULE_URL = "https://pro-football-reference.com/years/" + str(YEAR) + "/games.htm"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

schedule_page = requests.get(WEEKLY_SCHEDULE_URL, headers=headers) # Pull the HTML for the year's schedule
schedule_soup = BeautifulSoup(schedule_page.content, 'html5lib') # Parse the HTML using BeautifulSoup
schedule_table = schedule_soup.find('table')
schedule_table_rows = schedule_table.find_all('tr', attrs={'class': None})[1:273] # Get all regular season rows in the schedule table

browser = webdriver.Chrome() # Some elements take time to load, using Selenium for parsing box scores
for table_row in schedule_table_rows:
    week_number = int(table_row.find('th', attrs={'data-stat': 'week_num'}).decode_contents()) # Obtain the week number from the row
    box_score_url = "https://pro-football-reference.com" + table_row.find('td', attrs={'data-stat': 'boxscore_word'}).find('a').get('href') # Obtain the link to the box score
    sleep(5) # Sleep to adhere to rate limiting
    box_score_page = browser.get(box_score_url) # Navigate to the box score
    box_score_soup = BeautifulSoup(browser.page_source, 'html5lib') # Parse the page with BeautifulSoup
    game_header = box_score_soup.find('h1').decode_contents() # Obtain the header for the game to extract the team names
    print(game_header) # Log the game header
    # Parse the team names
    split_game_header = game_header.split(" at ")
    vis = split_game_header[0]
    home = split_game_header[1].split(" -")[0]
    game_name = str(YEAR) + "-Week " + str(week_number) + "-" + vis + "-" + home

    # Parse the scoring summary into a CSV
    scoring_summary = box_score_soup.find('table', attrs={'id': 'scoring'})
    scoring_summary_df = pd.read_html(StringIO(str(scoring_summary)))[0]
    scoring_summary_df.to_csv('output/' + game_name + "/Scoring-Summary-" + game_name + ".csv", index=False)

    # Parse the Play by Play into a CSV
    play_by_play = box_score_soup.find('table', attrs={'id': 'pbp'})
    play_by_play_df = pd.read_html(StringIO(str(play_by_play)))[0]
    play_by_play_df = play_by_play_df[~play_by_play_df['Quarter'].str.contains("Quarter", na=False)]
    play_by_play_df.to_csv('output/' + game_name + "/Play-By-Play-" + game_name + ".csv", index=False)

    # Parse the offensive statistics into a CSV
    offense = box_score_soup.find('table', attrs={'id': 'player_offense'})
    offense_df = pd.read_html(StringIO(str(offense)))[0]
    columns_of_interest = ["Player", "Tm"]
    [columns_of_interest.append(idx[0] + "_" + idx[1]) for idx in offense_df.columns[2:]]
    offense_df.columns = columns_of_interest
    offense_df = offense_df[~offense_df["Passing_Cmp"].isin(["Passing", "Cmp"])]
    offense_df.to_csv('output/' + game_name + "/Offense-Statistics-" + game_name + ".csv", index=False)

    # Parse the defensive statistics into a CSV
    defense = box_score_soup.find('table', attrs={'id': 'player_defense'})
    defense_df = pd.read_html(StringIO(str(defense)))[0]
    columns_of_interest = ["Player", "Tm"]
    [columns_of_interest.append(idx[0] + "_" + idx[1]) for idx in defense_df.columns[2:]]
    defense_df.columns = columns_of_interest
    defense_df = defense_df[~defense_df["Def Interceptions_Int"].isin(["Int", "Def Interceptions"])]
    defense_df.to_csv('output/' + game_name + "/Defense-Statistics-" + game_name + ".csv", index=False)

    # Parse the kick/punt returns into a CSV
    returns = box_score_soup.find('table', attrs={'id': 'returns'})
    if returns is not None:
        returns_df = pd.read_html(StringIO(str(returns)))[0]
        columns_of_interest = ["Player", "Tm"]
        [columns_of_interest.append(idx[0] + "_" + idx[1]) for idx in returns_df.columns[2:]]
        returns_df.columns = columns_of_interest
        returns_df = returns_df[~returns_df["Kick Returns_Yds"].isin(["Yds", "Kick Returns"])]
        returns_df.to_csv('output/' + game_name + "/Return-Statistics-" + game_name + ".csv", index=False)

    # Parse the special teams statistics into a CSV
    special_teams = box_score_soup.find('table', attrs={'id': 'kicking'})
    if special_teams is not None:
        special_teams_df = pd.read_html(StringIO(str(special_teams)))[0]
        columns_of_interest = ["Player", "Tm"]
        [columns_of_interest.append(idx[0] + "_" + idx[1]) for idx in special_teams_df.columns[2:]]
        special_teams_df.columns = columns_of_interest
        special_teams_df = special_teams_df[~special_teams_df["Scoring_XPM"].isin(["XPM", "Scoring"])]
        special_teams_df.to_csv('output/' + game_name + "/Special-Teams-Statistics-" + game_name + ".csv", index=False)