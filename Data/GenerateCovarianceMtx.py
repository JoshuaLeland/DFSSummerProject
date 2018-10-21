import numpy as np 
import scipy.sparse as sci 
import pandas as pd 


def GenerateCovarianceMtx(PredictionFile, FilePath):
	#Get the Team list.
	Teams = np.unique(PredictionFile[:,1])
	npMtx = PredictionFile
	COV_IND = 6

	#Lists to create sparse mtx.
	row = []
	column = []
	data = []

	numPlayers, nfeatures = npMtx.shape
	#OutArray = np.zeros((numPlayers,numPlayers))

	#Get the Starting Pitchers and add them too diagnol
	npMtxPitchers = PredictionFile[PredictionFile[:,2]=='SP']
	n, d = npMtxPitchers.shape
	for i in range(n):
		Name = npMtxPitchers[i,0]
		i1 = np.where(npMtx[:,0]==Name)[0][0]
		row.append(i1)
		column.append(i1)
		data.append(npMtxPitchers[i,5])
		#OutArray[i1,i1] = npMtxPitchers[i,5]

	for team in Teams:
		#Get the Batters for this team
		npMtxTeam = PredictionFile[PredictionFile[:,1]==team]

		#a
		npMtxTeam = npMtxTeam[npMtxTeam[:,2]!='SP']

		#Open the covariance file.
		CovarTeam = pd.read_csv(FilePath+team+'COV.csv')
		CovarTeam.drop(columns='Unnamed: 0', inplace=True)
		CovarTeam = CovarTeam.as_matrix()

		#Get the shape of the players on the slate.
		n, d = npMtxTeam.shape

		#Cycle through the players.
		for i in range(n):
			Name1 = npMtxTeam[i,0]
			i1 = np.where(npMtx[:,0]==Name1)[0][0]
			Pred1 = npMtx[i1,4]
			Var1 = npMtx[i1,5]

			for j in range(i, n):
				Name2 = npMtxTeam[j,0]
				i2 = np.where(npMtx[:,0]==Name2)[0][0]
				Pred2 = npMtx[i2,4]
				Var2 = npMtx[i2,5]

				#Find the covariance value in the CovTeam File
				if Name1 in CovarTeam[CovarTeam[:,0]==Name2,1]:
					CovName1 = CovarTeam[CovarTeam[:,0]==Name2]
					CovName2 = CovName1[CovName1[:,1]==Name1]
					Corr = CovName2[0][COV_IND]

				
				if Name2 in CovarTeam[CovarTeam[:,0]==Name1,1]:
					CovName1 = CovarTeam[CovarTeam[:,0]==Name1]
					CovName2 = CovName1[CovName1[:,1]==Name2]
					Corr = CovName2[0][COV_IND]

				#Symetric matrix so we add the indicies twice. - Coefficent is for half normal.
				#Cov = Corr*Pred1*Pred2*.85
				if Pred1 > 10:
					Var1=Var1*1.2
				elif Pred1 > 9:
					Var1=Var1*1.1

				if Pred2 > 10:
					Var2=Var2*1.2
				elif Pred2 > 9:
					Var1=Var1*1.1


				Cov=Corr*np.sqrt(Var1)*np.sqrt(Var2)
				row.append(i1)
				column.append(i2)
				data.append(Cov)
				

				if i1 != i2:
					row.append(i2)
					column.append(i1)
					data.append(Cov)
					#OutArray[i2,i1] = Cov

	#Done the loop return the sparse
	#print(max(data))
	return sci.coo_matrix((np.array(data),(np.array(row),np.array(column))), shape=(numPlayers,numPlayers))
	#return OutArray