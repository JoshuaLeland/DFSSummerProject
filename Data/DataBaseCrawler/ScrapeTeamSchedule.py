import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

class ScheduleScraper:
	def __init__(self, team, year):
		self.Link = 'https://www.fangraphs.com/teams/'+team+'/schedule/?season='+year
		self.team = team
		self.year = year

	def scrapeSchedule(self):
		soup = BeautifulSoup(requests.get(self.Link).text, "html.parser")
		tags1 = soup.find_all("div","team-schedule-table")[0]
		tags2=tags1.find_all("tr")
		Game1=tags2[1].find_all("td")

		#Scrape the HTML
		Data = []
		for i in range(1, len(tags2)):
			Row=[]
			Game1 = tags2[i].find_all("td")
			#Date Home/Away Opp WinP W/L TeamRuns OppSuns TeamStart OppStart
			Date = Game1[0].find("span", "date-full").get_text()
			if(Game1[1].get_text()=='vs'):
				Home = 'Home'
			else:
				Home = 'Away'
			Opp = Game1[2].get_text()
			try:
				WinP = float(Game1[3].get_text().strip('%'))
			except:
				WinP = -1

			Win = Game1[4].get_text()
			try:
				TeamRuns = float(Game1[5].get_text())
				OppRuns = float(Game1[6].get_text())
			except:
				TeamRuns=-1
				OppRuns=-1
				
			TeamStarterID = Game1[7].find_all('a')[0].get('href').split('=')[1]
			TeamStarterName = Game1[7].find_all('a')[0].get_text()
			OppStarterID = Game1[8].find_all('a')[0].get('href').split('=')[1]
			OppStarterName = Game1[8].find_all('a')[0].get_text()
			Row = [Date, Home, Opp, WinP, Win, TeamRuns, OppRuns, TeamStarterID, TeamStarterName, OppStarterID, OppStarterName]
			Data.append(Row)
		self.TeamSchedule = pd.DataFrame(columns=['Date', 'Home/Away', 'Opp', 'Win Prob', 'Win/Loss', 'TeamRuns', 'Opp Runs', 'StarterID', 'StarterName', 'OppStarterID', 'OppStarterName'], data=Data)

	def exportSchedule(self,filepath):
		self.TeamSchedule.to_csv(filepath+self.team+self.year+'Schedule.csv')