import os # Directory Creation
import requests # HTTP requests for web scraping
from time import sleep # Adhering to rate limiting
from bs4 import BeautifulSoup # HTML scraping library
import re 

YEAR = 2016
WEEKLY_SCHEDULE_URL = ["https://espn.co.uk/nfl/fixtures/_/week/" + str(i) + "/year/" + str(YEAR) for i in range(1, 19)]

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'
}

week_number = 1
# Iterate through all weeks of the NFL season
for url in WEEKLY_SCHEDULE_URL:
    print("Processing Week", week_number)
    sleep(60) # Sleep 5 seconds for rate limiting adherance
    week_page = requests.get(url, headers=headers) # Obtain webpage data for that week's schedule
    week_soup = BeautifulSoup(week_page.content, 'html5lib') # Parse webpage with BeautifulSoup
    game_links = week_soup.find_all("a", attrs={"name": "&lpos=nfl:schedule:score"}) # Obtain all links to the games for that weeks
    game_urls = [link.get('href') for link in game_links] # Get the URLs for each game that week from the links
    game_ids = [game_url.split("/")[5] for game_url in game_urls]
    recap_urls = ["https://www.espn.co.uk/nfl/recap/_/gameId/" + id for id in game_ids]
    # Iterate through all recaps
    for recap_url in recap_urls:
        sleep(5) # Sleep 5 seconds for rate limiting adherance
        recap_page = requests.get(recap_url, headers=headers) # Obtain webpage data for that game's recap
        recap_soup = BeautifulSoup(recap_page.content, 'html5lib') # Parse webpage with BeautifulSoup
        team_names = recap_soup.find_all('h2', attrs={'class': 'ScoreCell__TeamName ScoreCell__TeamName--displayName db'}) # Obtain both elements containing the team names
        team_names = [name.decode_contents() for name in team_names] # Extract the team names from the HTML elements
        print("Processing", team_names[0], "vs.", team_names[1], "Week", week_number, YEAR)
        game_name = str(YEAR) + "-Week " + str(week_number) + "-" + team_names[0] + "-" + team_names[1] 
        if not os.path.exists("output/" + game_name):
            os.makedirs("output/" + game_name) # If the directory does not exist, create it
        story_soup = recap_soup.find('div', attrs={'class': "Story__Body t__body"}) # Get element containing the recap
        if story_soup is not None:
            text_elements = story_soup.find_all("p") # Obtain all text elements in the recaps
            raw_text = [p.decode_contents().strip() for p in text_elements] # Break all text elements down into strings
            raw_text_string = "\n".join(raw_text) # Join all strings together
            processed_string = re.sub(r"<[^>]*>", "", raw_text_string) # Remove all HTML tags from the article
            # Create and write the article to a file
            recap_text_file = open("output/" + game_name + "/" + game_name + ".txt", 'w', encoding="utf-8")
            recap_text_file.write(processed_string)
            recap_text_file.close()
        else:
            os.rmdir("output/" + game_name)
    week_number += 1