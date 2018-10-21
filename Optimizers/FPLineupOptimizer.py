from ortools.linear_solver import pywraplp
import pandas as pd
import numpy as np

#This is probably going to be completely re-written to optimize for projected FPPs and variance.
class FPLineUpOptimizer:

	def __init__(self, dataframe, Dtype='DKbb'):
	# Only supports DraftBoard Basketball.

		#Initalize the solver.
		self.solver = pywraplp.Solver('SolveIntgerProblem', pywraplp.Solver.CBC_MIXED_INTEGER_PROGRAMMING)
		self.type = Dtype
		
		if self.type == 'DKbb':
			self.SalaryCap = 50000.00
			self.Iname = 0
			self.ITeam = 1
			self.IPosition = 2
			self.Iprice = 3
			self.IPoints = 4
			self.uncert = 5
		self.constVect = []
		self.varList = []

		#Store data and labels.
		self.playerdata = dataframe.values
		#self.labels = dataframe.values
		self.ndata, self.nfeat = self.playerdata.shape

	def setVarables(self):
		#Set the variable List.
		#Set up variables
		#Initalize the variable lists. If players play two positisions we split them and add a constraint
		varList2 = []
		for i in range(self.ndata):
			if len(self.playerdata[i,self.IPosition].split('/')) < 2 :
				self.varList.append(self.solver.IntVar(0.0, 1.0 , self.playerdata[i,self.Iname]))
			else:
				# self.playerdata[i,self.IPosition] = self.playerdata[i,self.IPosition].split('/')[0]
				# self.varList.append(self.solver.IntVar(0.0, 1.0 , self.playerdata[i,self.Iname]))
				#Split both of these vectors.
				datavect = self.playerdata[i]
				datavect2 = self.playerdata[i].copy()

				#Modify the names by adding position tags.
				pos = datavect[self.IPosition].split('/')
				datavect[self.Iname] = datavect[self.Iname] + ' ' +pos[0]
				datavect2[self.Iname] = datavect2[self.Iname] + ' ' + pos[1]
				datavect[self.IPosition] = pos[0]
				datavect2[self.IPosition] = pos[1]

				#Add the new touple - This is way to tough
				self.playerdata = np.append(self.playerdata, [datavect2.T], axis=0)

				#Add the variables
				var1 = self.solver.IntVar(0.0, 1.0 , datavect[self.Iname])
				var2 = self.solver.IntVar(0.0, 1.0 , datavect2[self.Iname])
				self.varList.append(var1)
				varList2.append(var2)

				#Add a constraint to have only of the variables allowed.
				SplitConstraint = self.solver.Constraint(0.0, 1.0)
				SplitConstraint.SetCoefficient(var1, 1.0)
				SplitConstraint.SetCoefficient(var2, 1.0)

				#Add the vars and constraint to the list
				self.constVect.append(SplitConstraint)
		self.varList = self.varList + varList2
		self.ndata, self.nfeat = self.playerdata.shape


	def setConstraints(self):

		if self.type == 'DKbb':
			#Salary Constraint 
			self.constVect.append(self.salaryConstraint(self.SalaryCap))

			#P constraint - We want greater than so flip the signs. 1 Pitcher.
			self.constVect.append(self.positionConstraint( ['SP'], -2, -self.solver.infinity(), 'GT'))
			self.constVect.append(self.positionConstraint( ['SP'], self.solver.infinity(), 2, 'LT'))

			#C constraint - We want greater than so flip the signs. 1 Catcher.
			self.constVect.append(self.positionConstraint( ['C'], -1, -self.solver.infinity(), 'GT'))
			self.constVect.append(self.positionConstraint( ['C'], self.solver.infinity(), 1, 'LT'))

			#1B constraint - We want greater than so flip the signs. 1 First baseman.
			self.constVect.append(self.positionConstraint( ['1B'], -1, -self.solver.infinity(), 'GT'))
			self.constVect.append(self.positionConstraint( ['1B'], self.solver.infinity(), 1, 'LT'))

			#2B constraint - We want greater than so flip the signs. 1 Second baseman.
			self.constVect.append(self.positionConstraint( ['2B'], -1, -self.solver.infinity(), 'GT'))
			self.constVect.append(self.positionConstraint( ['2B'], self.solver.infinity(), 1, 'LT'))

			#3B constraint - We want greater than so flip the signs. 1 Third baseman.
			self.constVect.append(self.positionConstraint( ['3B'], -1, -self.solver.infinity(), 'GT'))
			self.constVect.append(self.positionConstraint( ['3B'], self.solver.infinity(), 1, 'LT'))

			#SS constraint - We want greater than so flip the signs. 1 Third baseman.
			self.constVect.append(self.positionConstraint( ['SS'], -1, -self.solver.infinity(), 'GT'))
			self.constVect.append(self.positionConstraint( ['SS'], self.solver.infinity(), 1, 'LT'))

			#OF constraint - We want greater than so flip the signs. 3 Third baseman.
			self.constVect.append(self.positionConstraint( ['LF','CF', 'RF', 'OF'], -3, -self.solver.infinity(), 'GT'))
			self.constVect.append(self.positionConstraint( ['LF','CF', 'RF', 'OF'], self.solver.infinity(), 3, 'LT'))

			#Player Constraint
			constTop,constBottom = self.playerConstraint(10.0)
			self.constVect.append(constTop)
			self.constVect.append(constBottom)

	#Set FP Cost function - Will set an EV cost function later.
	def setFPCostFunction(self, lamb=None):
		if self.type == 'DKbb':
			if lamb == None:
				self.objective = self.solver.Objective()
				for i in range(self.ndata):
					self.objective.SetCoefficient(self.varList[i],float(self.playerdata[i,self.IPoints]))
				self.objective.SetMaximization()
			else:
				self.objective = self.solver.Objective()
				for i in range(self.ndata):
					obj = float(self.playerdata[i,self.IPoints]) - lamb*float(self.playerdata[i,self.uncert])
					self.objective.SetCoefficient(self.varList[i],obj)
				self.objective.SetMaximization()



	#Solve the system
	def solve(self):
		status = self.solver.Solve()
		return status

	#Return the player list
	def returnPlayers(self):
		playerList = []

		#If the solver set the variable to one it wants us to play it.
		for i in range(self.ndata):
			if(self.varList[i].solution_value() == 1):
				playerList.append(self.varList[i].name())

		#Pull the Position Tags back off.
		detaggedPlayers = []
		for players in playerList:
			names = players.split(' ')
			detaggedPlayers.append(names[0] + ' ' + names[1])
			
		return detaggedPlayers

	def returnPoints(self):
		#Return
		return self.solver.Objective().Value()

	def positionConstraint(self, pos, topC, bottomC, bound='GT'):
		#Make the constrain.
		Const = self.solver.Constraint(bottomC, topC)
		nPos = len(pos)

		#Set the bound type Greater than or Less than
		if bound == 'GT':
			coff = -1
		else:
			coff = 1

		#Loop through the data
		for i in range(self.ndata):
			#Initally set the coefficent to zero - change if it fits into the position.
			Const.SetCoefficient(self.varList[i], 0)

			#If it fits the position type.
			for j in range(nPos):
				if self.playerdata[i,self.IPosition] == pos[j]:
					Const.SetCoefficient(self.varList[i], coff)

		return Const

	def playerConstraint(self, topC):
		#Player constraint - Top
		PlayerConstP = self.solver.Constraint(0.0, topC)
		for i in range(self.ndata):
			PlayerConstP.SetCoefficient(self.varList[i], 1)

		#Player constraint - Bottom
		PlayerConstN = self.solver.Constraint(-topC, 0.0)
		for i in range(self.ndata):
			PlayerConstN.SetCoefficient(self.varList[i], -1)

		return PlayerConstP, PlayerConstN

	def salaryConstraint(self, salaryConst):
		#Initalize the salary constraint.
		salaryConst = self.solver.Constraint(0.0, salaryConst)

		#Set the salary for each player.
		for i in range(self.ndata):
			salaryConst.SetCoefficient(self.varList[i], self.playerdata[i,self.Iprice])
			
		return salaryConst
