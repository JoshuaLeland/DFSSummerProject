import pandas as pd 
import Data.DraftKingsPredictionsParsing as DK
import Optimizers.FPLineupOptimizer as opt
import GeneralTools.LineUpCrawler.LineUpCrawler as LC

class MLBGenerateLineUps:
	def __init__(self, Date):

		#Set up filepaths
		FanGBatter = 'Data/FanGraphPred/'+Date+'/FanGraphsBatter'+Date+'.csv'
		FanGPitcher = 'Data/FanGraphPred/'+Date+'/FanGraphsPitcher'+Date+'.csv'
		RotoGPredBatter = 'Data/RotoGPred/'+Date+'/mlb-hitter'+Date+'.csv'
		RotoGPredPitcher = 'Data/RotoGPred/'+Date+'/mlb-pitcher'+Date+'.csv'
		Salaries = 'Data/DKSalaries/DKSalaries'+Date+'.csv'
		Variance = 'Data/DataBaseCrawler/MasterVarianceList.csv'
		DKPredictions = 'Data/DraftKingsPredictions/'

		#Set up the parser.
		self.parser = DK.ParseDKPredictions(Salaries)
		self.parser.addPredictions(FanGPitcher, FanGBatter,'FG')
		self.parser.addPredictions(RotoGPredPitcher, RotoGPredBatter, 'Roto')
		self.parser.addVariance(Variance)
		self.parser.exportProjections('DKProjections'+Date, DKPredictions)

		#Set up Crawler
		self.crawler = LC.LineUpCrawler()

	def returnOptLineUps(self, Known=False, lamb=None, Pred='Avg'):

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

		#Assign Variance
		OptProjections['Var'] = self.parser.FormattedSalaries['Var']

		#Use known Line up info
		if Known == True:
			OutProjections = OptProjections[OptProjections['Name'].isin(self.crawler.getPlayers())]
		else:
			OutProjections = OptProjections

		#Run the optimizer.
		self.Optimizers = opt.FPLineUpOptimizer(OutProjections)
		self.Optimizers.setVarables()
		self.Optimizers.setConstraints()
		self.Optimizers.setFPCostFunction(lamb)
		self.Optimizers.solve()

		#Return the 
		return OutProjections[OutProjections['Name'].isin(self.Optimizers.returnPlayers())]

	def returnSetOptLineUps(self, LambSet, Known=False, Pred='Avg'):
		#Generate a Set of Solutions.
		Solutions = []
		for lamb in LambSet:
			LineUp = self.returnOptLineUps(Known, lamb, Pred)
			SumPred = sum(LineUp['FP'])
			SumVar = sum(LineUp['Var'])
			Solution = [LineUp, SumPred, SumVar, lamb]
			Solutions.append(Solution)
		return Solutions