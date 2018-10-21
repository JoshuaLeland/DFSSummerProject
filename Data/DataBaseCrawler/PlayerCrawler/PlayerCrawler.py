import requests
from bs4 import BeautifulSoup
import re
import pandas as pd

class TeamRoster:
	def __init__(self,batterLink, pitcherLink, teamName):
		self.teamName = teamName
		self.batterLink = batterLink
		self.pitcherLink = pitcherLink
		self.battingRoster = self.getBatterList()
		self.pitchingRoster = self.getPitcherList()

	def getBatterList(self):
		r = requests.get(self.batterLink)
		soup = BeautifulSoup(r.text, "html.parser")
		tableAlt = soup.find_all("tr", "rgAltRow")
		table = soup.find_all("tr", "rgRow")
		TeamList = []
		for i in range(0, len(table)):
			row = []
			gridrow = table[i].find_all("td", "grid_line_regular")
			if gridrow[1].find("a").get('href').find("&position=P") == -1:
				#Get the Name and Link
				row.append(gridrow[1].text)
				row.append(self.teamName)
				row.append(gridrow[1].find("a").get('href').split("?")[1].split("&")[0].split("=")[1])
				row.append(gridrow[1].find("a").get('href').replace("statss","statsd") + '&type=1&gds=&gde=&season=all')
				for j in range(2,len(gridrow)):
					row.append(gridrow[j].text)
				TeamList.append(row)
		for i in range(0, len(tableAlt)):
			row = []
			gridrow = tableAlt[i].find_all("td", "grid_line_regular")
			if gridrow[1].find("a").get('href').find("&position=P") == -1:
				#Get the Name and Link
				row.append(gridrow[1].text)
				row.append(self.teamName)
				row.append(gridrow[1].find("a").get('href').split("?")[1].split("&")[0].split("=")[1])
				row.append(gridrow[1].find("a").get('href').replace("statss","statsd") + '&type=1&gds=&gde=&season=all')
				for j in range(2,len(gridrow)):
					row.append(gridrow[j].text)
				TeamList.append(row)

		return pd.DataFrame(data=TeamList,columns=['Name','Team','ID' ,'Link','G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','IBB','SO','HBP','SF','SH','GDP','SB','CS','AVG'])

	def getPitcherList(self):
		r = requests.get(self.pitcherLink)
		soup = BeautifulSoup(r.text, "html.parser")
		tableAlt = soup.find_all("tr", "rgAltRow")
		table = soup.find_all("tr", "rgRow")
		TeamList = []
		for i in range(0, len(table)):
			row = []
			gridrow = table[i].find_all("td", "grid_line_regular")
			if gridrow[1].find("a").get('href').find("&position=P") != -1:
				#Get the Name and Link
				row.append(gridrow[1].text)
				row.append(self.teamName)
				row.append(gridrow[1].find("a").get('href').split("?")[1].split("&")[0].split("=")[1])
				row.append(gridrow[1].find("a").get('href').replace("statss","statsd") + '&type=1&gds=&gde=&season=all')
				for j in range(2,len(gridrow)):
					row.append(gridrow[j].text)
				TeamList.append(row)
		for i in range(0, len(tableAlt)):
			row = []
			gridrow = tableAlt[i].find_all("td", "grid_line_regular")
			if gridrow[1].find("a").get('href').find("&position=P") != -1:
				#Get the Name and Link
				row.append(gridrow[1].text)
				row.append(self.teamName)
				row.append(gridrow[1].find("a").get('href').split("?")[1].split("&")[0].split("=")[1])
				row.append(gridrow[1].find("a").get('href').replace("statss","statsd") + '&type=1&gds=&gde=&season=all')
				for j in range(2,len(gridrow)):
					row.append(gridrow[j].text)
				TeamList.append(row)

		return pd.DataFrame(data=TeamList,columns=['Name','Team', 'ID', 'Link','W','L','ERA','G','GS','CG','ShO','SV','HLD','BS','IP','TBF','H','R','ER','HR','BB','IBB','HBP','WP','BK','SO'])

	def returnBatterList(self):
		return self.battingRoster

	def returnPitcherList(self):
		return self.pitchingRoster

	def returnTeam(self):
		return self.teamName