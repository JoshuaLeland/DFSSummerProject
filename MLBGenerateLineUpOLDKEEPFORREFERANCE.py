import Optimizers.FPLineupOptimizer as opt 
import LineUpCrawler.LineUpCrawler as lc 
import MLBProjectionParser.MLBProjectionsParser as parse 

class MLBLineUpGenerator:

	def __init__(self, batterProjFile, pitcherProjFile, salariesFile):

		#Set up the parser.
		self.parser = parse.MLBProjectionsParser(pitcherProjFile,batterProjFile)
		self.parser.joinSalaries(salariesFile)

		#Set up the crawler.
		self.crawler = lc.LineUpCrawler()


	def exportPredictions(self, filename, location):
		self.parser.exportProjections(filename, location, 'sal')

	def getTeams(self, Rtype="all"):
		#We want to get the list of teams on the slate.
		if(Rtype=="all"):
			return self.parser.Projections.Team.unique()

		#Get list of the teams that released their line up.
		if(Rtype=="lineup"):
			return [x for x in self.crawler.getTeamList(True) if x in self.parser.Projections.Team.unique()]

		#Get list of teams with no line up.
		if(Rtype=="nolineup"):
			return [x for x in self.crawler.getTeamList(False) if x in self.parser.Projections.Team.unique()]
		

	def getLineUp(self, knownLineUp):
		#If knownlineup is true we select from the player pool which we know
		if(knownLineUp==True):
			OutProjections = self.parser.ProjSal[self.parser.ProjSal['Name'].isin(self.crawler.getPlayers())]

		#If it is false we select from the entire pool.
		else:
			OutProjections = self.parser.ProjSal

		return OutProjections

	def returnOptLineUps(self,known, lamb=0.0):
		self.optimizer = opt.FPLineUpOptimizer(self.getLineUp(known), 'DKbb')
		self.optimizer.setVarables()
		self.optimizer.setConstraints()
		self.optimizer.setFPCostFunction(lamb)
		self.optimizer.solve()

		return self.optimizer.returnPlayers()
	
	def getPoints(self):
		return self.optimizer.getPoints()

	def addProjections(self, PitcherFile, BattlerFile, Projtype='Roto'):
		self.parser.addProjections(PitcherFile, BattlerFile, Projtype)

	def returnSetOptLineUps(self, known, lambs):
		#Do a line search for Average points and uncertainty.
		Lineups = []
		for lamb in lambs:
			lineup = []
			#Solve the system.
			players = self.returnOptLineUps(known,lamb)
			#Get the players in the line up.
			playersProj = self.parser.ProjSal[self.parser.ProjSal['Name'].isin(players)]

			#Calculate the points.
			points = sum(playersProj['DKAvg'])

			#Calculate the uncertainty
			uncert = sum(playersProj['Var'])

			#Salary                                                                                                                                                 
			salary = sum(playersProj['Salary'])

			#Put in a list.
			lineup.append(points)
			lineup.append(uncert)
			lineup.append(salary)
			lineup.append(lamb)
			lineup.append(self.optimizer.returnPoints())
			lineup.append(players)
			Lineups.append(lineup)

		return Lineups

