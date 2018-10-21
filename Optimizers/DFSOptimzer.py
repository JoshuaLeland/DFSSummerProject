from gurobipy import *
import pandas as pd 
import numpy as np 

#Solves the Binary Quadraic Programming problem with
#This will need to be refactored to be more general.
class DFSOptimizer:
	#Initalize the set up.
	def __init__(self, dataframe):

		#Set up the blank model.
		self.m = Model("")

		#Save our projections file.
		self.projections = dataframe.as_matrix()

		#Save Constants -- Only set up for DK right now.
		self.cName = 0
		self.cTeam = 1
		self.cPos = 2
		self.cSalary = 3
		self.cProj = 4
		self.cVar = 5

	def splitPlayers(self):
		#We want to split players who can play multiple positions.
		SplitPlayers = []
		n, d = self.projections.shape
		for i in range(n):
			Pos = self.projections[i,self.cPos].split('/')
			if len(Pos) > 1:
				Copy = self.projections[i].copy()
				self.projections[i,self.cPos] = Pos[0]
				Copy[self.cPos] = Pos[1]
				Copy[self.cName] = Copy[self.cName] + ' ' + Pos[1]
				SplitPlayers.append(Copy)

		#Save the split players.
		splitplayers = np.array(SplitPlayers)

		#Save the total list 
		self.totalplayer = np.concatenate([self.projections, splitplayers])

		#return split players.
		return splitplayers

	def setupVariables(self):
		#Add the Variables to the model.
		self.varPlayers = self.m.addVars(self.totalplayer[:,self.cName], vtype=GRB.BINARY)

		#Sometimes I need to do this in a notebook so I put this here jsut incase.
		self.m.update()

	def splitConstraints(self, splitplayers):
		#Put in position constraints. -- We don't want one player taking up too slots.
		for name in splitplayers[:,0]:
			sNames = name.split(' ')
			#print(name)
			try:
			    #Get the matching platers.
				player1 = self.varPlayers.get(name)
				secondName = sNames[0]
				for i in range(1,len(sNames)):
					secondName = secondName + ' '+sNames[i]
				player2 = self.varPlayers.get(secondName)
			    
				#Add Constraint
				self.m.addConstr(player1 + player2 <=1,sNames[0]+' '+sNames[1] +' Split C' )
			except:
				print(name+ ' could not be added to split constraints')
		self.m.update()

	def salaryConstraints(self, Salary):
		#Put our variables into a np array and just use the dot product.
		Salaries = np.array([x[self.cSalary]*self.varPlayers[x[self.cName]] for x in self.totalplayer])
		self.m.addConstr(np.sum(Salaries)<=Salary, 'Salary C')
		self.m.update()

	def setPositionConstraints(self, Position, numPositon, cType='equal'):
		#Need to make this more general later.
		#Build NP Arrays for each position
		PosList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]== Position])

		#Add Position Constraints.
		if cType == 'equal':
			self.m.addConstr(np.sum(PosList) == numPositon, Position + 'Constraint')

		if cType == 'less':
			self.m.addConstr(np.sum(PosList) < numPositon, Position + 'Constraint')

		if cType == 'greater':
			self.m.addConstr(np.sum(PosList) > numPositon, Position + 'Constraint')

		if cType == 'lessEq':
			self.m.addConstr(np.sum(PosList) <= numPositon, Position + 'Constraint')

		if cType == 'greaterEq':
			self.m.addConstr(np.sum(PosList) >= numPositon, Position + 'Constraint')
		self.m.update()

	def setTotalPlayerConstraints(self, NumPlayers):
		self.m.addConstr(np.sum(np.array(self.m.getVars())) == NumPlayers)

	def TeamConstraints(self, NumTeam, ExcludedPosition, GameList=None):
		#List of teams
		Teams = np.unique(self.totalplayer[:,self.cTeam])

		#If GameList isn't empty we put in a non
		for team in Teams:
			TeamMates = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cTeam]==team and x[self.cPos] != ExcludedPosition])
			TeamC = np.sum(TeamMates)
			if GameList is not None:
				#Get Opposing team
				if team in GameList[:,0]:
					oppteam = GameList[GameList[:,0] == team,1]

				if team in GameList[:,1]:
					oppteam = GameList[GameList[:,1] == team,0]

				#Get SP for other team - We force the opposite Position to fill the teams hitter requirement so we aren't picking line ups that are pitching against eachother..
				OppTeamPos = np.array([self.varPlayers[x[self.cName]]*NumTeam for x in self.totalplayer if x[self.cTeam]==oppteam and x[self.cPos] == ExcludedPosition])

				#Update constraints
				TeamC = TeamC + np.sum(OppTeamPos)

			if TeamMates.size > 0:
				self.m.addConstr(TeamC <= NumTeam, team +' C')

		self.m.update()

	def MatchUpConstraints(self, Positon,Num, GameList):
		Teams = np.unique(self.totalplayer[:,self.cTeam])
		for team in Teams:
			#Get player with this position
			if GameList is not None:
				if team in GameList[:,0]:
					oppteam = GameList[GameList[:,0] == team,1]

				if team in GameList[:,1]:
					oppteam = GameList[GameList[:,1] == team,0]

				MatchUp1 = np.sum(np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cTeam]==team and x[self.cPos] == Positon]))
				MatchUp2 = np.sum(np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cTeam]==oppteam and x[self.cPos] == Positon]))
				if MatchUp1 is not None and MatchUp2 is not None:
					#MatchUp=np.concatenate((MatchUp1,MatchUp2), axis=None)
					MatchC = MatchUp1+MatchUp2
					#print(MatchC)
					self.m.addConstr(MatchC <= Num)
					

	def PlayerConstraints(self, PlayerInfo, numPlayers, Name):
		#TODO GET BOTH POSITONAL PLAYERS
		namelist = []
		for player in self.totalplayer:
			names = player[self.cName].split(' ')
			name = names[0]+' '+names[1]
			if name in PlayerInfo:
				namelist.append(player[self.cName])

		PlayersC = np.array([self.varPlayers[x] for x in namelist])
		self.m.addConstr(np.sum(PlayersC) <= numPlayers, Name +'C')
		self.m.update()

	def setCostFunction(self, CovarianceMtx, gamma, PopVect=None):
		#Get the expectation vector.
		EVect = np.array([x[self.cProj]*self.varPlayers[x[self.cName]] for x in self.totalplayer])
		ObjMu = np.sum(EVect)
		self.CovMtx = CovarianceMtx

		#Get the objective function.
		Players = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer])
		M1 = np.dot(Players, self.CovMtx.toarray())
		ObjCov = np.dot(Players,M1)

		#Set the objective function.
		obj = ObjMu + gamma*ObjCov

		#Add Pop Data
		self.PopVect = PopVect
		if PopVect is not None:
			popMean = PopVect[0]
			popVar = PopVect[1]
			popCov = PopVect[2]
			obj = obj - popMean + gamma*(popVar - 2*np.dot(Players,popCov))


		#Set the cost function.
		self.m.setObjective(obj, GRB.MAXIMIZE)

	def solve(self):
		self.m.optimize()

	def getVariance(self):
		n,d = self.totalplayer.shape
		VarValues = np.zeros(n)
		for i in range(n):
			name = self.totalplayer[i,self.cName]
			var = self.varPlayers[name]
			if var.x==1:
				VarValues[i]=1
		if self.PopVect is not None:
			Var = self.PopVect[1]
			CovV = -2*np.dot(self.PopVect[2],VarValues)
		else:
			Var = 0
			CovV = 0
		return np.dot(np.dot(self.CovMtx.toarray(),VarValues), VarValues)+Var+CovV

	def EvPoints(self):
		#Get the selected players
		Output = []
		for players in self.totalplayer:
			name = players[self.cName]
			var = self.varPlayers[name]
			if var.x==1:
				Output.append(players[self.cProj])
		if self.PopVect is not None:
			popMean = self.PopVect[0]
		else:
			popMean = 0

		return sum(Output) - popMean

	def getPlayers(self):
		#Get the selected players
		Output = []
		for players in self.totalplayer:
			name = players[self.cName]
			var = self.varPlayers[name]
			if var.x==1:
				Output.append(name)

		#Trim the position tages off.
		detaggedPlayers = []
		for players in Output:
			names = players.split(' ')
			detaggedPlayers.append(names[0] + ' ' + names[1])

		return detaggedPlayers


