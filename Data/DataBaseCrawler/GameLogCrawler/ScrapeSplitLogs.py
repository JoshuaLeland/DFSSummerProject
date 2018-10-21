import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np

class BatterSplitLog:
	def __init__(self, LinkStub):
		self.StatsSL = 'https://www.fangraphs.com/' + LinkStub
		self.CanExport = True

	def scrapeSplitLogs(self):
		rSplit = requests.get(self.StatsSL)
		soupSplit = BeautifulSoup(rSplit.text, "html.parser")
		SplitHandedStd=[]
		StdTable=soupSplit.find("table",id="SeasonSplits1_dgSeason1_ctl00").find_all('td', 'grid_line_regular')
		for i in range(8):
			Line = []
			for j in range(22):
				try:
					Line.append(float(StdTable[22*(i)+j].get_text().strip("%")))
				except:
					Line.append(StdTable[22*(i)+j].get_text())
			SplitHandedStd.append(Line)
		try:
			SplitHandedStdDF = pd.DataFrame(data=SplitHandedStd[0:6], columns=['Season','Handedness','G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','IBB','SO','HBP','SF','SH','GDP','SB','CS','AVG'])
			SplitHomeAwayStdDF = pd.DataFrame(data=SplitHandedStd[6:8], columns=['Season','Home/Away','G','AB','PA','H','1B','2B','3B','HR','R','RBI','BB','IBB','SO','HBP','SF','SH','GDP','SB','CS','AVG'])
		except:
			self.CanExport = False
			print("Can't Scrape this split log!")

		SplitHandedAdv=[]
		StdTable=soupSplit.find("table",id="SeasonSplits1_dgSeason2_ctl00").find_all('td', 'grid_line_regular')
		for i in range(8):
			Line = []
			for j in range(15):
				try:
					Line.append(float(StdTable[15*(i)+j].get_text().strip("%")))
				except:
					 Line.append(StdTable[15*(i)+j].get_text())
			SplitHandedAdv.append(Line)
		try:
			SplitHandedAdvDF = pd.DataFrame(data=SplitHandedAdv[0:6], columns=['Season','Handedness','BB%','K%','BB/K','AVG','OBP','SLG','OPS','ISO','BABIP','wRC','wRAA','wOBA','wRC+'])
			SplitHomeAwayAdvDF = pd.DataFrame(data=SplitHandedAdv[6:8], columns=['Season','Home/Away','BB%','K%','BB/K','AVG','OBP','SLG','OPS','ISO','BABIP','wRC','wRAA','wOBA','wRC+'])
		except:
			self.CanExport = False
			print("Can't Scrape this split log!")
		try:
			self.SplitHandedBatter = pd.merge(SplitHandedStdDF,SplitHandedAdvDF, on=['Season', 'Handedness', 'AVG'])
			self.SplitHomeAwayBatter = pd.merge(SplitHomeAwayStdDF,SplitHomeAwayAdvDF, on=['Season', 'Home/Away', 'AVG'])
		except:
			self.CanExport = False
			print('Merge failed! with link: '+self.StatsSL)

	def exportGL(self, filename, path, ltype='Both'):
		if self.CanExport == True and ltype=='Hand' :
			self.SplitHandedBatter.to_csv(path+'/'+filename+'HandSL.csv')
		if self.CanExport == True and ltype=='HomeAway' :
			self.SplitHomeAwayBatter.to_csv(path+'/'+filename+'HomeAwaySL.csv')
		if self.CanExport == True and ltype=='Both' :
			self.SplitHomeAwayBatter.to_csv(path+'/'+filename+'HomeAwaySL.csv')
			self.SplitHandedBatter.to_csv(path+'/'+filename+'HandSL.csv')

class PitcherSplitLog:
	def __init__(self,LinkStub):
		self.StatsSL = 'https://www.fangraphs.com/' + LinkStub
		self.CanExport = True

	def scrapeSplitLogs(self):
		rSplit = requests.get(self.StatsSL)
		soupSplit = BeautifulSoup(rSplit.text, "html.parser")
		#Get Standard Split Stats
		SplitHandedStd=[]
		StdTable=soupSplit.find("table",id="SeasonSplits1_dgSeason1_ctl00").find_all('td', 'grid_line_regular')
		for i in range(4):
			Line = []
			for j in range(19):
				try:
					Line.append(float(StdTable[19*(i)+j].get_text().strip("%")))
				except:
					Line.append(StdTable[19*(i)+j].get_text())
			SplitHandedStd.append(Line)
		try:
			self.SplitHandedStdDF = pd.DataFrame(data=SplitHandedStd[0:2], columns=['Season','Handedness','IP','ERA','TBF','H','2B','3B','R','ER','HR','BB','IBB','HBP','SO','AVG','OBP','SLG','wOBA'])
			self.SplitHomeAwayStdDF=pd.DataFrame(data=SplitHandedStd[2:4], columns=['Season','Home/Away','IP','ERA','TBF','H','2B','3B','R','ER','HR','BB','IBB','HBP','SO','AVG','OBP','SLG','wOBA'])
		except:
			self.CanExport = False
			print("Can't Scrape this split log!")

		#Get Advanced Split Stats
		SplitHandedAdv=[]
		StdTable=soupSplit.find("table",id="SeasonSplits1_dgSeason2_ctl00").find_all('td', 'grid_line_regular')
		for i in range(4):
			Line = []
			for j in range(15):
				try:
					Line.append(float(StdTable[15*(i)+j].get_text().strip("%")))
				except:
					try:
						Line.append(StdTable[15*(i)+j].get_text())
					except:
						Line.append(-1)
			SplitHandedAdv.append(Line)
		try:
			self.SplitHandedAdvDF=pd.DataFrame(data=SplitHandedAdv[0:2], columns=['Season','Handedness','K/9','BB/9','K/BB','HR/9','K%','BB%','K-BB%','AVG','WHIP','BABIP','LOB%','FIP','xFIP'])
			self.SplitHomeAwayAdvDF=pd.DataFrame(data=SplitHandedAdv[2:4], columns=['Season','Home/Away','K/9','BB/9','K/BB','HR/9','K%','BB%','K-BB%','AVG','WHIP','BABIP','LOB%','FIP','xFIP'])
		except:
			self.CanExport = False
			print("Can't Scrape this split log!")
		try:
			self.SplitHandedPitcher = pd.merge(self.SplitHandedStdDF,self.SplitHandedAdvDF, on=['Season', 'Handedness'])
			self.SplitHomeAwayPitcher = pd.merge(self.SplitHomeAwayStdDF,self.SplitHomeAwayAdvDF, on=['Season', 'Home/Away'])
		except:
			self.CanExport = False
			print('Split merge failed! with Link: '+ self.StatsSL)


	def exportGL(self, filename, path, ltype='Both'):
		if self.CanExport == True and ltype=='Hand' :
			self.SplitHandedPitcher.to_csv(path+'/'+filename+'HandSL.csv')
		if self.CanExport == True and ltype=='HomeAway' :
			self.SplitHomeAwayPitcher.to_csv(path+'/'+filename+'HomeAwaySL.csv')
		if self.CanExport == True and ltype=='Both' :
			self.SplitHomeAwayPitcher.to_csv(path+'/'+filename+'HomeAwaySL.csv')
			self.SplitHandedPitcher.to_csv(path+'/'+filename+'HandSL.csv')