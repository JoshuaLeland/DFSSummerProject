import pandas as pd 
import numpy as np 

class GenerateCovarianceFile:
	def __init__(self, BatterRoster):
		RosterList = pd.read_csv(BatterRoster)
		self.MasterList = RosterList[['Name', 'Team', 'ID']]
		self.Teams = self.MasterList.Team.unique()
		VarList = pd.read_csv("MasterVarianceList.csv")
		self.MasterVarList = VarList[['Name', 'Team', 'Var']].as_matrix()

	def generateCovarianceTeam(self, Team):
		#Get The Player List
		PlayerList = self.MasterList[self.MasterList['Team']==Team]
		n, d = PlayerList.shape
		TeamCovList = []
		for i in range(n):
			#Get Player 1 info -- Saving all this info because it is liekly a predictor of Covariance for when we don't have enough count data.
			#Get the Indexes
			Indexes = PlayerList.index
			Player1Name = PlayerList['Name'][Indexes[i]]
			Player1ID = PlayerList['ID'][Indexes[i]]
			Player1DF = pd.read_csv('./GameLogs/Batters/'+str(Player1ID)+'GL.csv')
			Player1AvgBat = Player1DF['AVG'][0]
			Player1AvgBO = np.mean(pd.to_numeric(Player1DF['BO'].values[1:]))
			Player1DF = Player1DF[['Date', 'Team','DKfp']].drop(index=0)
			Player1Var = self.MasterVarList[self.MasterVarList[:,0]==Player1Name, 2][0]


			#print(Player1Var)
			for j in range(i, n):
				#Player 2 info
				Player2Name = PlayerList['Name'][Indexes[j]]
				Player2ID = PlayerList['ID'][Indexes[j]]
				Player2DF = pd.read_csv('./GameLogs/Batters/'+str(Player2ID)+'GL.csv')
				Player2AvgBat = Player2DF['AVG'][0]
				Player2AvgBO = np.mean(pd.to_numeric(Player2DF['BO'].values[1:]))
				Player2DF = Player2DF[['Date', 'Team','DKfp']].drop(index=0)
				Player2Var = self.MasterVarList[self.MasterVarList[:,0]==Player2Name, 2][0]

				#Merge the DF
				MergedDF = Player1DF.merge(Player2DF, left_on=['Date', 'Team'], right_on=['Date', 'Team'])
				Samples = [MergedDF['DKfp_x'].values, MergedDF['DKfp_y'].values]

				#Get Covariance
				#Through Data visualization the Covariance has no significant dependance on differance in batting order
				#Appears to be Normal, use mean of 6.6 when count data is too low.
				if len(MergedDF) > 200 or Player1Name==Player2Name:
					if Player1Name==Player2Name:
						corr = 1
						#cov = Player1Var
					else:
						#cov = np.cov(Samples)[0][1]
						corr = np.corrcoef(Samples)[0][1]
				else:
					corr = 0.21009176*Player1AvgBat + 0.08794302*Player2AvgBat - 0.00119284*np.abs(Player1AvgBO - Player2AvgBO) + 0.06123468 #Found empirically.
					#cov = np.sqrt(Player1Var)*np.sqrt(Player2Var)*corr
				TeamCovList.append([Player1Name, Player2Name, Team, Player1AvgBat, Player2AvgBat, np.abs(Player1AvgBO - Player2AvgBO) , corr, len(MergedDF)])

		return pd.DataFrame(data=TeamCovList, columns=['Name1', 'Name2', 'Team', 'BAvg1', 'BAvg2', 'BO Differance', 'Corr', 'Count'])

	def exportCovariances(self, Location):

		for team in self.Teams:
			TeamCov = self.generateCovarianceTeam(team)
			TeamCov.to_csv(Location + team + 'COV.csv')




