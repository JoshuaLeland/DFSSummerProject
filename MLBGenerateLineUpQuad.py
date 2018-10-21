import pandas as pd 
import Data.DraftKingsPredictionsParsing as DK
import Optimizers.GurobiLineUpOptimizer as opt
import GeneralTools.LineUpCrawler.LineUpCrawler as LC
from Data.GenerateCovarianceMtx import GenerateCovarianceMtx


class MLBGenerateLineUpsQuad:
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
		self.parser.exportProjections('DKProjections'+Date, self.DKPredictions)

		#Set up Crawler
		self.crawler = LC.LineUpCrawler()

	def returnOptLineUps(self, Known=False, lamb=0.0, Pred='Avg'):
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
			OutProjections = OptProjections[OptProjections['Name'].isin(self.crawler.getPlayers())]
		else:
			OutProjections = OptProjections

		#Run the Gurobi Optimizer
		self.Optimizers = opt.FPQuadatricIntOpt(OutProjections)
		splitplayers = self.Optimizers.splitPlayers()
		self.Optimizers.setupVariables()
		self.Optimizers.splitConstraints(splitplayers)
		self.Optimizers.salaryConstraints()
		self.Optimizers.setPlayerConstraints()
		self.Optimizers.setPositionConstraints()
		self.Optimizers.hitterConstraints()
		CovMtx = GenerateCovarianceMtx(self.Optimizers.totalplayer,self.CovFilePath)
		#print(CovMtx.diagonal())
		self.Optimizers.setCostFunction(CovMtx, lamb)

		self.Optimizers.solve()

		#Return the players.
		return OutProjections[OutProjections['Name'].isin(self.Optimizers.getPlayers())]

	def returnSetOptLineUps(self, LambSet, Known=False, Pred='Avg'):
		#Generate a Set of Solutions.
		Solutions = []
		for lamb in LambSet:
			LineUp = self.returnOptLineUps(Known, lamb, Pred)
			SumPred = sum(LineUp['FP'])
			SumVar = self.Optimizers.getVariance()
			Solution = [LineUp, SumPred, SumVar, lamb]
			Solutions.append(Solution)
		return Solutions