import pandas as pd 
import numpy as np 


def Abv2Name(x):
	return {
		'ARI': 'Diamondbacks',
		'ATL': 'Braves',
		'BAL': 'Orioles',
		'CHC': 'Cubs',
		'CLE': 'Indians',
		'COL': 'Rockies',
		'DET': 'Tigers',
		'MIA': 'Marlins',
		'HOU': 'Astros',
		'LAA': 'Angels',
		'LAD': 'Dodgers',
		'MIL': 'Brewers',
		'MIN': 'Twins',
		'NYM': 'Mets',
		'NYY': 'Yankees',
		'OAK': 'Athletics',
		'PHI': 'Phillies',
		'PIT': 'Pirates',
		'SD': 'Padres',
		'SF': 'Giants',
		'SEA': 'Mariners',
		'STL': 'Cardinals',
		'TEX': 'Rangers',
		'TB': 'Rays',
		'TOR': 'Blue Jays',
		'WAS': 'Nationals',
		'BOS': 'Red Sox',
		'CIN': 'Reds',
		'CWS': 'White Sox',
		'KC': 'Royals',
		'CHW': 'White Sox',
		'KCR' : 'Royals',
		'SDP' : 'Padres',
		'SFG' : 'Giants',
		'TBR' : 'Rays'
	}[x]

class ParseDKPredictions:

	def __init__(self, DKSalaries):
		#Format the salaries to the following format
		#Name  		Team  Position  Salary ex.
		#Jim Jones  Mets     SP       5000
		self.RawFile = pd.read_csv(DKSalaries)
		self.RawFile['Team'] = self.RawFile.apply(lambda x: Abv2Name(x['TeamAbbrev']), axis=1)
		self.FormattedSalaries = pd.DataFrame()
		self.FormattedSalaries['Name'] = self.RawFile['Name']
		self.FormattedSalaries['Team'] = self.RawFile['Team']
		self.FormattedSalaries['Position'] = self.RawFile['Position']
		self.FormattedSalaries['Salary'] = self.RawFile['Salary']

	def addPredictions(self, PitcherFile, BatterFile, Type='FG'):
		if Type == 'FG':
			BatterPredDF = pd.read_csv(BatterFile)
			PitcherPredDF = pd.read_csv(PitcherFile)
			BatterPredDF.drop(columns=['Game','Pos','PA','H','1B','2B','3B','HR','R','RBI','SB','CS','BB','SO','Yahoo','FanDuel', 'playerid'], inplace=True)
			PitcherPredDF.drop(columns=['Game','W','IP','TBF','H','1B','2B','3B','HR','BB','SO','Yahoo','FanDuel', 'playerid'], inplace=True)
			FanGraphPred = pd.concat([BatterPredDF,PitcherPredDF]).rename(columns={'DraftKings':'DKFG'})
			self.FormattedSalaries = self.FormattedSalaries.merge(FanGraphPred, how='left', left_on=['Name', 'Team'], right_on=['Name', 'Team']).dropna(subset=['DKFG'])

		if Type == 'Roto':
			BatterPredDF = pd.read_csv(BatterFile, header=None)
			PitcherPredDF = pd.read_csv(PitcherFile, header=None)
			BatterPredDF['Team'] = BatterPredDF.apply(lambda x: Abv2Name(x[2]), axis=1)
			PitcherPredDF['Team'] = PitcherPredDF.apply(lambda x: Abv2Name(x[2]), axis=1)
			BatterPredDF.rename(columns={0:'Name',7:'DKRoto'}, inplace=True )
			PitcherPredDF.rename(columns={0:'Name',7:'DKRoto'}, inplace=True )
			BatterPredDF.drop(columns={1, 2, 3, 4, 5, 6}, inplace=True)
			PitcherPredDF.drop(columns={1, 2, 3, 4, 5, 6}, inplace =True)
			RotoPred = pd.concat([BatterPredDF,PitcherPredDF])
			self.FormattedSalaries = self.FormattedSalaries.merge(RotoPred, how='left', left_on=['Name', 'Team'], right_on=['Name', 'Team']).dropna(subset=['DKRoto'])

		if Type == 'TheBAT':
			BatBatterPred = pd.read_csv(BatterFile)
			BatPitcherPred = pd.read_csv(PitcherFile)
			BatBatterPred = BatBatterPred[['NAME', 'TEAM', 'FPTS']]
			BatBatterPred['TEAM']=BatBatterPred.apply(lambda x: Abv2Name(x['TEAM']), axis=1)
			BatBatterPred.columns = ['Name', 'Team', 'BATPred']
			BatPitcherPred = BatPitcherPred[['NAME', 'TEAM', 'FPTS']]
			BatPitcherPred['TEAM'] = BatPitcherPred.apply(lambda x: Abv2Name(x['TEAM']), axis=1)
			BatPitcherPred.columns = ['Name', 'Team', 'BATPred']
			BATPred = pd.concat([BatBatterPred,BatPitcherPred])
			self.FormattedSalaries = self.FormattedSalaries.merge(BATPred, how='left', left_on=['Name', 'Team'], right_on=['Name', 'Team']).dropna(subset=['BATPred'])


	def addVariance(self, VarianceFile):
		VarFile = pd.read_csv(VarianceFile)
		self.FormattedSalaries = self.FormattedSalaries.merge(VarFile, how='left', left_on=['Name', 'Team'], right_on=['Name', 'Team'])
		self.FormattedSalaries.drop(columns=['VarSV', 'Unnamed: 0'], inplace=True)
		self.FormattedSalaries.dropna(subset=['Var'], inplace = True)

	def exportProjections(self, name, location):
		self.FormattedSalaries.to_csv(location+name+'.csv')
