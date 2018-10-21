import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

class BatterGameLog:
	def __init__(self, LinkStub):
		self.StandardStatsGL = 'https://www.fangraphs.com/' + LinkStub
		self.CanExport = True

	def scrapeGL(self, StdTable, StdTableAlt, Lim):
		GameLog = []
		n = len(StdTable)
		for i in range(n):
			#i == 0 is the total line.
			row = []
			gridrow = StdTable[i].find_all("td")
			for j in range(len(gridrow)):
				if j < Lim :
					 row.append(gridrow[j].text)
				else:
					try:
						row.append(float(gridrow[j].text.strip("%")))
					except:
						row.append(gridrow[j].text)
			GameLog.append(row)
		n = len(StdTableAlt)
		for i in range(n):
			#i == 0 is the total line.
			row = []
			gridrow = StdTableAlt[i].find_all("td")
			for j in range(len(gridrow)):
				if j < Lim :
					row.append(gridrow[j].text)
				else:
					try:
						row.append(float(gridrow[j].text))
					except:
						row.append(gridrow[j].text)             
			GameLog.append(row)
		return GameLog

	def scrapeStdGL(self):
		soupStd = BeautifulSoup(requests.get(self.StandardStatsGL).text, "html.parser")
		StdTable = soupStd.find_all("tr", "rgRow")
		StdTableAlt = soupStd.find_all("tr", "rgAltRow")

		GameLog = self.scrapeGL(StdTable,StdTableAlt,4)

		try:
			self.StandardGL = pd.DataFrame(data=GameLog, columns=['Date', 'Team','Opp','BO','Pos','G','AB','PA','H','1B', '2B', '3B','HR','R','RBI','BB','IBB','SO', 'HBP', 'SF', 'SH', 'GDP', 'SB', 'CS', 'AVG'])
			self.StandardGL['DKfp'] = 0.0
			Sum = 0
			rows, col = self.StandardGL.shape
			DKFPVect = np.zeros(rows)
			
			DKFPVect[1:rows] = 3*self.StandardGL['1B'][1:rows] + 5*self.StandardGL['2B'][1:rows] + 8*self.StandardGL['3B'][1:rows] + 10*self.StandardGL['HR'][1:rows] + 2*self.StandardGL['RBI'][1:rows] + 2*self.StandardGL['R'][1:rows] + 2*self.StandardGL['BB'][1:rows] + 2*self.StandardGL['HBP'][1:rows] + 5*self.StandardGL['SB'][1:rows]
			DKFPVect[0] = sum(DKFPVect[1:rows])
			self.StandardGL['DKfp'] = DKFPVect
		except:
			print('Error makeing GameLog for %s' % self.StandardStatsGL)
			self.CanExport = False

	def scrapeAdvGL(self):
		rAdv = requests.get(self.StandardStatsGL.replace("type=1", "type=2"))
		soupAdv = BeautifulSoup(rAdv.text, "html.parser")
		AdvTable = soupAdv.find_all("tr", "rgRow")
		AdvTableAlt = soupAdv.find_all("tr", "rgAltRow")
		GameLog = self.scrapeGL( AdvTable, AdvTableAlt, 4)
		try:
			GameLogAdvPit = pd.DataFrame(data=GameLog, columns=['Date','Team','Opp','BO','Pos','BB%','K%','BB/K','AVG','OBP','SLG','OPS','ISO','Spd','BABIP','wSB','wRC','wRAA','wOBA', 'wRC+'])
			self.StandardAdv = GameLogAdvPit
		except:
			print('Error making GameLog for %s' % self.StandardStatsGL.replace("type=1", "type=2"))
			self.CanExport = False

	def exportGL(self, filename, path, ltype='Std'):
		if self.CanExport == True and ltype=='Std' :
			self.StandardGL.to_csv(path+'/'+filename+'.csv')
		if self.CanExport == True and ltype=='Adv' :
			self.StandardAdv.to_csv(path+'/'+filename+'.csv')
		if self.CanExport == True and ltype=='Both' :
			OutDF = pd.merge(self.StandardGL, self.StandardAdv, on=['Date', 'Team', 'Opp', 'BO', 'Pos', 'AVG'])
			OutDF.to_csv(path+'/'+filename+'.csv')

class PitcherGameLog:
	def __init__(self, LinkStub):
		self.StandardStatsGL = 'https://www.fangraphs.com/' + LinkStub
		self.CanExport = True

	def scrapeGL(self, StdTable, StdTableAlt, Lim):
		GameLog = []
		n = len(StdTable)
		for i in range(n):
			#i == 0 is the total line.
			row = []
			gridrow = StdTable[i].find_all("td")
			for j in range(len(gridrow)):
				if j < Lim :
					 row.append(gridrow[j].text)
				else:
					try:
						row.append(float(gridrow[j].text.strip("%")))
					except:
						row.append(gridrow[j].text)
			GameLog.append(row)
		n = len(StdTableAlt)
		for i in range(n):
			#i == 0 is the total line.
			row = []
			gridrow = StdTableAlt[i].find_all("td")
			for j in range(len(gridrow)):
				if j < Lim :
					row.append(gridrow[j].text)
				else:
					try:
						row.append(float(gridrow[j].text))
					except:
						row.append(gridrow[j].text)             
			GameLog.append(row)
		return GameLog


	def scrapeStdGL(self):
		rStd = requests.get(self.StandardStatsGL)
		soupStd = BeautifulSoup(rStd.text, "html.parser")
		StdTable = soupStd.find_all("tr", "rgRow")
		StdTableAlt = soupStd.find_all("tr", "rgAltRow")
		GameLog = self.scrapeGL( StdTable, StdTableAlt,3)
		try:
			GameLogPDPit = pd.DataFrame(data=GameLog, columns=['Date','Team','Opp','GS','W','L','ERA','G','GS_x','CG','ShO','SV','HLD','BS','IP','TBF','H','R','ER','HR','BB','IBB','HBP','WP','BK','SO','GSv2'])
			#Calculate DK fps
			rows, cols = GameLogPDPit.shape
			Sum = 0
			FPVect = np.zeros(rows)
			FPVect[1:rows] = 2.25*GameLogPDPit['IP'][1:rows].values + 2*GameLogPDPit['SO'][1:rows].values + 4*GameLogPDPit['W'][1:rows].values - 2*GameLogPDPit['ER'][1:rows].values- 0.6*GameLogPDPit['BB'][1:rows].values - 0.6*GameLogPDPit['HBP'][1:rows].values
			for i in range(1,rows):
				if GameLogPDPit['IP'][i] == 9:
					FPVect[i] = FPVect[i] + 2.5
					if GameLogPDPit['ER'][i] == 0:
						FPVect[i] = FPVect[i] + 2.5
				if GameLogPDPit['H'][i] == 0:
					FPVect[i] = FPVect[i] + 5
			FPVect[0] = sum(FPVect[1:rows])
			GameLogPDPit['DKfp'] = FPVect
			self.StandardGL = GameLogPDPit
		except:
			print('Error makeing GameLog for %s' % self.StandardStatsGL)
			self.CanExport = False

	def scrapeAdvGL(self):
		rAdv = requests.get(self.StandardStatsGL.replace("type=1", "type=2"))
		soupAdv = BeautifulSoup(rAdv.text, "html.parser")
		AdvTable = soupAdv.find_all("tr", "rgRow")
		AdvTableAlt = soupAdv.find_all("tr", "rgAltRow")
		GameLog = self.scrapeGL( AdvTable, AdvTableAlt,3)
		try:
			GameLogAdvPit = pd.DataFrame(data=GameLog, columns=['Date','Team','Opp','GS','K/9','BB/9','K/BB','HR/9','K%','BB%','K-BB%','AVG','WHIP','BABIP','LOB%','ERA-','FIP-','FIP'])
			self.StandardAdv = GameLogAdvPit
		except:
			print('Error making GameLog for %s' % self.StandardStats.GLreplace("type=1", "type=2"))
			self.CanExport = False


	def exportGL(self, filename, path, ltype='Std'):
		if self.CanExport == True and ltype=='Std' :
			self.StandardGL.to_csv(path+'/'+filename+'.csv')
		if self.CanExport == True and ltype=='Adv' :
			self.StandardAdv.to_csv(path+'/'+filename+'.csv')
		if self.CanExport == True and ltype=='Both' :
			OutDF = pd.merge(self.StandardGL, self.StandardAdv, on=['Date', 'Team', 'Opp', 'GS'])
			OutDF.to_csv(path+'/'+filename+'.csv')
