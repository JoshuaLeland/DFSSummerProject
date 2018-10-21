import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

#Gets the list of teams and the links to the teams for a given year
def getTeamInfo():

	CONST_R_LINK = 'https://www.fangraphs.com/leaders.aspx?pos=all&stats=bat&lg=all&qual=0&type=8&season=2018&month=0&season1=2018&ind=0&team=0,ts&rost=&age=&filter=&players=0'
	r = requests.get(CONST_R_LINK)
	soup = BeautifulSoup(r.text, "html.parser")
	table = soup.find_all("td", "grid_line_regular")
	TeamInfo = []
	teamLinksBat =[]
	teamname = []
	for i in range(0,30):
	    teamLinksBat.append(table[i*17+1].find("a").get('href').replace("type=8","type=0"))
	    teamname.append(table[i*17+1].text)
	teamLinksPit = []
	for links in teamLinksBat:
		teamLinksPit.append(links.replace("bat", "pit"))
	dataIn = {'TeamName': teamname, 'TeamLinksBat' : teamLinksBat,'TeamLinksPit' : teamLinksPit}
	dataframe = pd.DataFrame(data=dataIn)
	dataframe = dataframe[['TeamName', 'TeamLinksBat', 'TeamLinksPit']]

	return dataframe