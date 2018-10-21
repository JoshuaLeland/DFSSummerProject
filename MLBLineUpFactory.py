import pandas as pd 
import Data.DraftKingsPredictionsParsing as DK
import Optimizers.DFSOptimzer as opt
import GeneralTools.LineUpCrawler.LineUpCrawler as LC
from Data.GenerateCovarianceMtx import GenerateCovarianceMtx
import scipy.stats as stats
import numpy as np


class MLBLineUpFactory:
	def __init__(self, Date, theBat=False):

		#Set up filepaths
		self.FanGBatter = 'Data/FanGraphPred/'+Date+'/FanGraphsBatter'+Date+'.csv'
		self.FanGPitcher = 'Data/FanGraphPred/'+Date+'/FanGraphsPitcher'+Date+'.csv'
		self.RotoGPredBatter = 'Data/RotoGPred/'+Date+'/mlb-hitter'+Date+'.csv'
		self.RotoGPredPitcher = 'Data/RotoGPred/'+Date+'/mlb-pitcher'+Date+'.csv'
		self.TheBATPredBatter ='Data/The-BAT/'+'the-bat-hitters-'+Date+'.csv'
		self.TheBATPredPitcher ='Data/The-BAT/'+'the-bat-pitchers-'+Date+'.csv'
		self.Salaries = 'Data/DKSalaries/DKSalaries'+Date+'.csv'
		self.Variance = 'Data/DataBaseCrawler/MasterVarianceList.csv'
		self.DKPredictions = 'Data/DraftKingsPredictions/'
		self.CovFilePath = 'Data/DataBaseCrawler/TeamCovariance/'

		#Set up the parser.
		self.parser = DK.ParseDKPredictions(self.Salaries)
		self.parser.addPredictions(self.FanGPitcher, self.FanGBatter,'FG')
		self.parser.addPredictions(self.RotoGPredPitcher, self.RotoGPredBatter, 'Roto')
		if theBat == True:
			self.parser.addPredictions(self.TheBATPredPitcher, self.TheBATPredBatter, 'TheBAT')

		self.parser.addVariance(self.Variance)
		#self.parser.exportProjections('DKProjections'+Date, self.DKPredictions)

		#Set up Crawler
		self.crawler = LC.LineUpCrawler()

	def getSlateInfo(self):
		GameSlate = self.parser.RawFile['Game Info'].unique()

		AwayTeamsAbv=[]
		HomeTeamsAbv=[]
		for games in GameSlate:
			AwayTeamsAbv.append(games.split('@')[0])
			HomeTeamsAbv.append(games.split('@')[1].split(' ')[0])

		AwayTeams=[]
		HomeTeams=[]
		for teams in AwayTeamsAbv:
			AwayTeams.append(DK.Abv2Name(teams))
		for teams in HomeTeamsAbv:
			HomeTeams.append(DK.Abv2Name(teams))

		SlateInfo = np.array([HomeTeams,AwayTeams]).T
		return SlateInfo


		#Initalize the Optimizer
	def InitalizeOptimizer(self, Known=False, Pred='Avg'):
		#Make a dataframe with the Predictions we want.
		OptProjections = pd.DataFrame()		
		OptProjections['Name'] = self.parser.FormattedSalaries['Name']
		OptProjections['Team'] = self.parser.FormattedSalaries['Team']
		OptProjections['Position'] = self.parser.FormattedSalaries['Position']
		OptProjections['Salary'] = self.parser.FormattedSalaries['Salary']

		#Assign the projections.
		if Pred == 'Avg':
			OptProjections['FP'] = 0.5*(self.parser.FormattedSalaries['DKFG'] + self.parser.FormattedSalaries['DKRoto'])

		if Pred == 'FG':
			OptProjections['FP'] = self.parser.FormattedSalaries['DKFG']

		if Pred == 'Roto':
			OptProjections['FP'] = self.parser.FormattedSalaries['DKRoto']

		if Pred == 'TheBAT':
			OptProjections['FP'] = self.parser.FormattedSalaries['BATPred']

		#Assign Variance
		OptProjections['Var'] = self.parser.FormattedSalaries['Var']

		#Use known Line up info
		if Known == True:
			self.OutProjections = OptProjections[OptProjections['Name'].isin(self.crawler.getPlayers())]
		else:
			self.OutProjections = OptProjections

		#Run the Gurobi Optimizer
		self.Optimizers = opt.DFSOptimizer(self.OutProjections)
		splitplayers = self.Optimizers.splitPlayers()
		self.Optimizers.setupVariables()
		self.Optimizers.splitConstraints(splitplayers)
		self.Optimizers.salaryConstraints(50000)
		self.Optimizers.setTotalPlayerConstraints(10)

		#Set up the DK MLB Constraints.
		self.Optimizers.setPositionConstraints('SP',2)
		self.Optimizers.setPositionConstraints('1B',1)
		self.Optimizers.setPositionConstraints('2B',1)
		self.Optimizers.setPositionConstraints('3B',1)
		self.Optimizers.setPositionConstraints('C',1)
		self.Optimizers.setPositionConstraints('SS',1)
		self.Optimizers.setPositionConstraints('OF',3)

		#Set up team constraints
		self.Optimizers.TeamConstraints(5,'SP', self.getSlateInfo())
		#self.Optimizers.MatchUpConstraints('SP', 1, self.getSlateInfo())

	def ReturnLineUps(self, PointBoundary, NumLineUps, botLamb, TopLamb, numLamb, playerC, popVect=None):
		LambdaSet = np.linspace(botLamb, TopLamb, num=numLamb)
		CovMtx = GenerateCovarianceMtx(self.Optimizers.totalplayer,self.CovFilePath)

		OutSolutions=[]
		for i in range(NumLineUps):
			#Generate Solution set.
			Solutions = []
			for lamb in LambdaSet:
				self.Optimizers.setCostFunction(CovMtx, lamb,popVect)
				self.Optimizers.solve()
				SumPred = self.Optimizers.EvPoints()
				SumVar = self.Optimizers.getVariance()
				LineUp = self.Optimizers.getPlayers()
				Solution = [LineUp, SumPred, SumVar, lamb]
				Solutions.append(Solution)

			ePoints = []
			Var = []
			for sol in Solutions:
				if sol[2] > 0:
					ePoints.append(sol[1])
					Var.append(sol[2])

			#Pick best solution
			Probs=[]
			for i in range(len(ePoints)):
				Probs.append(1-stats.norm.cdf(PointBoundary, loc=ePoints[i], scale=np.sqrt(Var[i])))
			iMaxProb = np.argmax(Probs)

			MaxProb = Probs[iMaxProb]
			DFLineUp = self.OutProjections[self.OutProjections['Name'].isin(Solutions[iMaxProb][0])]
			#DFLineUp = Solutions[iMaxProb][0]
			MeanOpt = Solutions[iMaxProb][1]
			VarOpt = Solutions[iMaxProb][2]
			Lambda = Solutions[iMaxProb][3]

			OutSolutions.append([DFLineUp,MeanOpt,VarOpt,MaxProb])

			#Add Solution constraint.
			self.Optimizers.PlayerConstraints(Solutions[iMaxProb][0], playerC, 'Player ' + str(i))

		#return the lineups
		return OutSolutions




