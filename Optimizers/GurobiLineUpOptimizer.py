from gurobipy import *
import pandas as pd 
import numpy as np 

#Solves the Binary Quadraic Programming problem with
#This will need to be refactored to be more general.
class FPQuadatricIntOpt:
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
		self.SALARY_CONST = 50000
		self.NUM_PLAYERS = 10
		self.HITTER_CONST = 5

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

	def salaryConstraints(self):
		#Put our variables into a np array and just use the dot product.
		Salaries = np.array([x[self.cSalary]*self.varPlayers[x[self.cName]] for x in self.totalplayer])
		self.m.addConstr(np.sum(Salaries)<=50000, 'Salary C')
		self.m.update()

	def setPositionConstraints(self):
		#Need to make this more general later.
		#Build NP Arrays for each position
		OFList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]=='OF'])
		SSList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]=='SS'])
		TBList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]=='3B'])
		SBList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]=='2B'])
		FBList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]=='1B'])
		CList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]=='C'])
		SPList = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cPos]=='SP'])

		#Add Position Constraints.
		self.m.addConstr(np.sum(OFList) ==3, 'OF Constraint')
		self.m.addConstr(np.sum(SSList) ==1, 'SS Constraint')
		self.m.addConstr(np.sum(TBList) ==1, '3B Constraint')
		self.m.addConstr(np.sum(SBList) ==1, '2B Constraint')
		self.m.addConstr(np.sum(FBList) ==1, '1B Constraint')
		self.m.addConstr(np.sum(CList) ==1, 'C Constraint')
		self.m.addConstr(np.sum(SPList) ==2, 'SP Constraint')
		self.m.update()

	def setPlayerConstraints(self):
		self.m.addConstr(np.sum(np.array(self.m.getVars())) == self.NUM_PLAYERS)


	def hitterConstraints(self):
		Teams = np.unique(self.totalplayer[:,self.cTeam])
		for team in Teams:
			TeamMates = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer if x[self.cTeam]==team and x[self.cPos] != 'SP'])
			if TeamMates.size > 0:
				self.m.addConstr(np.sum(TeamMates) <= self.HITTER_CONST, team+' Hitter C')
		self.m.update()


	def setCostFunction(self, CovarianceMtx, gamma):
		#Get the expectation vector.
		EVect = np.array([x[self.cProj]*self.varPlayers[x[self.cName]] for x in self.totalplayer])
		ObjMu = np.sum(EVect)
		self.CovMtx = CovarianceMtx
		#print(self.CovMtx.diagonal())

		#Get the objective function.
		Players = np.array([self.varPlayers[x[self.cName]] for x in self.totalplayer])
		M1 = np.dot(Players, self.CovMtx.toarray())
		#M1 = np.dot(Players, self.CovMtx)
		ObjCov = np.dot(Players,M1)

		#Set the objective function.
		obj = ObjMu + gamma*ObjCov

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
		return np.dot(np.dot(self.CovMtx.toarray(),VarValues), VarValues)

	def getPlayers(self):

		#Get the selected players
		OutPut = []
		for players in self.totalplayer:
			name = players[self.cName]
			var = self.varPlayers[name]
			if var.x==1:
				OutPut.append(name)

		#Trim the position tages off.
		detaggedPlayers = []
		for players in OutPut:
			names = players.split(' ')
			detaggedPlayers.append(names[0] + ' ' + names[1])

		return detaggedPlayers


