import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

class ScrapeMLBRoster:
	def __init__(self, year):
		#Get Teams
		Teams = pd.read_csv('MLBTeams2018.csv')
		self.Teams = Teams['TeamName'].values
		self.year = year

	def scrapeTeamRoster(self, Team):
		#Get the soup
		Link = 'https://www.fangraphs.com/teams/'+Team.replace(" ", "").lower()+'/stats?season='+str(self.year)
		soupStd = BeautifulSoup(requests.get(Link).text, "html.parser")

		#First index is batter.
		BatterSoup = soupStd.find_all('div', 'team-stats-table')[0]
		BatterLinks = BatterSoup.find_all('a')

		#Get the links for the team.
		BatterRoster = []
		for link in BatterLinks:
			Name = link.get_text()
			pLink = link.get('href')
			ID = pLink.split('=')[1].split('&')[0]
			Position = pLink.split('=')[2]
			Row = [Name,Team ,Link, int(ID), Position]
			BatterRoster.append(Row)

		TeamBattingRoster = pd.DataFrame(data=BatterRoster, columns=['Name', 'Team', 'Links','ID','Position'])
		TeamBattingRoster = TeamBattingRoster[TeamBattingRoster['Position']!='P']
		#First index is batter.
		PitcherSoup = soupStd.find_all('div', 'team-stats-table')[1]
		PitcherLinks = PitcherSoup.find_all('a')

		#Get the links for the team.
		PitcherRoster = []
		for link in PitcherLinks:
			Name = link.get_text()
			pLink = link.get('href')
			ID = pLink.split('=')[1].split('&')[0]
			Position = pLink.split('=')[2]
			Row = [Name,Team ,Link, int(ID), 'S'+Position]
			PitcherRoster.append(Row)

		TeamPitcherRoster = pd.DataFrame(data=PitcherRoster, columns=['Name', 'Team', 'Links','ID','Position'])

		return TeamBattingRoster, TeamPitcherRoster

	def ExportRosters(self,location):
		#Initalize the dataframs/
		OutBattingRoster = pd.DataFrame()
		OutPitchingRoster = pd.DataFrame()

		#Concat the team rosters.
		for team in self.Teams:
			NewBattingRoster, NewPitchingRoster = self.scrapeTeamRoster(team)
			OutBattingRoster=pd.concat([OutBattingRoster,NewBattingRoster])
			OutPitchingRoster=pd.concat([OutPitchingRoster,NewPitchingRoster])

		#Remove duplicates
		OutBattingRoster.drop_duplicates(subset=['ID'], inplace=True)
		OutPitchingRoster.drop_duplicates(subset=['ID'], inplace=True)
		
		#Store the CSV files.
		OutBattingRoster.to_csv(location+'BattingRoster'+str(self.year)+'.csv')
		OutPitchingRoster.to_csv(location+'PitchingRoster'+str(self.year)+'.csv')




