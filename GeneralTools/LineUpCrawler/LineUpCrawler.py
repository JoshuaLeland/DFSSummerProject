import requests
from bs4 import BeautifulSoup
import re

class LineUpCrawler:
	def __init__(self):
		#Class data.
		self.CONSTLINK = 'http://www.baseballpress.com/lineups'
		self.soup = BeautifulSoup(requests.get(self.CONSTLINK).text, "html.parser")
		self.players = []
		self.battingOrders = []
		self.TeamsWithLineup = []
		self.TeamsNoLineUp =[]

		#Class Flags
		self.parsedTeam = False
		self.parsedPlayers = False

	def parseTeams(self):
		#Get the HTML of teams with no line up.
		TeamNoLineUpHTML = self.soup.find_all("div", "team-name no-lineup")
		TeamLineUpHTML = self.soup.find_all("div", "team-name")

		#remove the no lineup HTML - problem with beautifulsoup
		TeamLineUpHTML = [x for x in TeamLineUpHTML if x not in TeamNoLineUpHTML]

		#Add the Team lineup
		for team in TeamLineUpHTML:
			self.TeamsWithLineup.append(team.text.strip())

		#Add the no line up team
		for team in TeamNoLineUpHTML:
			self.TeamsNoLineUp.append(team.text.strip())

		self.parsedTeam = True

	def parsePlayers(self):
		#Let the players link.
		playerlinks = self.soup.find_all("a", "player-link")

		#Parse a list of all the players.
		for player in playerlinks:
			self.players.append(player.text.strip())

    	#Parse the batting order
		BattingOrderHTML = self.soup.find_all("div", "players")

    	#Using Regex to get player names.
		for lineUps in BattingOrderHTML:
			templineup = lineUps.text.strip()
			self.battingOrders.append(re.findall('\w+\s\w+',templineup))

		self.parsedPlayers = True

	def getTeamList(self, wlineup):
		if(not self.parsedTeam):
			self.parseTeams()
    		
		if(wlineup):
			return self.TeamsWithLineup
		else:
			return self.TeamsNoLineUp

	def getPlayers(self):
		if(not self.parsedPlayers):
			self.parsePlayers()
		return self.players

	def getBattingOrders(self):
		if(not self.parsedPlayers):
			self.parsePlayers()
		return self.battingOrders
