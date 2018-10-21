
def QuickPopulationModel(Date, LineUpDiffFactor,TopPercent,minPointFact,numPlayers,numSims,Know):
	#For some reason theses need to be here.
	import MLBLineUpFactory as lineup
	import numpy as np
	import pandas as pd
	from Data.GenerateCovarianceMtx import GenerateCovarianceMtx

	#Calculate the 1 sect of line ups.
	RotoGLineUp = lineup.MLBLineUpFactory(Date, theBat=True)
	RotoGLineUp.InitalizeOptimizer(Known=Know, Pred='Roto')
	RotoLinePredUps=RotoGLineUp.ReturnLineUps(minPointFact,numPlayers,0,0,1,LineUpDiffFactor)

	#Calculate the 2 set of line ups.
	#FGLineUp = lineup.MLBLineUpFactory(Date, theBat=True)
	#FGLineUp.InitalizeOptimizer(Known=Know, Pred='FG')
	#FGLinePredUps=FGLineUp.ReturnLineUps(minPointFact,int(numPlayers/2),0,0,1,LineUpDiffFactor)

	#Use this so our player vectors line up
	BATLineUp = lineup.MLBLineUpFactory(Date, theBat=True)
	BATLineUp.InitalizeOptimizer(Known=Know, Pred='TheBAT')

	#Compile line ups
	#Put all the line ups into list
	lineUpList = []
	#for lineup in FGLinePredUps:
	#	lineUpList.append(lineup[0])
	for lineup in RotoLinePredUps:
		lineUpList.append(lineup[0])

	#Build Player vectors.
	players = []
	for lineup in lineUpList:
		ind = [np.where(BATLineUp.Optimizers.totalplayer==x)[0][0] for x in lineup['Name'].values]
		player = np.zeros(len(BATLineUp.Optimizers.totalplayer[:,0]))
		player[ind] = 1
		players.append(player)

	#Construct Order expected preformance for the TopPercent place
	G = []
	Values = []
	RSV = []
	Fraction = 1/(TopPercent/100)
	for i in range(numSims):
		Cov=GenerateCovarianceMtx(BATLineUp.Optimizers.totalplayer,'Data/DataBaseCrawler/TeamCovariance/')
		RS = np.random.multivariate_normal(BATLineUp.Optimizers.totalplayer[:,4].tolist(),Cov.todense())
		for i in range(len(RS)):
			if(BATLineUp.Optimizers.totalplayer[i,2]!='SP'):
				RS[i] = abs(RS[i])
		RealizedList = [sum(RS*x) for x in players]
		Slist = -np.sort(-np.array(RealizedList))
		value = Slist[int(len(Slist)/Fraction)]
		ind = np.where(RealizedList==value)[0][0]
		RSV.append(RS)
		G.append(players[ind]*RS)
		Values.append(value)

	Epoints = np.mean(Values)
	VPlayer = np.var(Values)

	#Model Covariance
	Gnp = np.array(G)
	RSVnp = np.array(RSV)
	Gr = np.mean(Gnp, axis=0)
	OutCov = []
	for i in range(len(Gr)):
		OutCov.append(np.cov(RSVnp[i,:],Gr)[0,1])

	return Epoints, VPlayer, OutCov

def GPPPopulationModel(Date, LineUpDiffFactor,TopPercent,minPointFact,numPlayers,numSims,Know):
	#For some reason theses need to be here.
	import MLBLineUpFactory as lineup
	import numpy as np
	import pandas as pd
	from Data.GenerateCovarianceMtx import GenerateCovarianceMtx

	#Calculate the 1 sect of line ups.
	RotoGLineUp = lineup.MLBLineUpFactory(Date, theBat=True)
	RotoGLineUp.InitalizeOptimizer(Known=Know, Pred='Roto')
	RotoLinePredUps=RotoGLineUp.ReturnLineUps(minPointFact,numPlayers,0,0.03,8,LineUpDiffFactor)

	#Calculate the 2 set of line ups.
	#FGLineUp = lineup.MLBLineUpFactory(Date, theBat=True)
	#FGLineUp.InitalizeOptimizer(Known=Know, Pred='FG')
	#FGLinePredUps=FGLineUp.ReturnLineUps(minPointFact,int(numPlayers/2),0,0.03,5,LineUpDiffFactor)

	#Use this so our player vectors line up
	BATLineUp = lineup.MLBLineUpFactory(Date, theBat=True)
	BATLineUp.InitalizeOptimizer(Known=Know, Pred='TheBAT')

	#Compile line ups
	#Put all the line ups into list
	lineUpList = []
	#for lineup in FGLinePredUps:
	#	lineUpList.append(lineup[0])
	for lineup in RotoLinePredUps:
		lineUpList.append(lineup[0])

	#Build Player vectors.
	players = []
	for lineup in lineUpList:
		ind = [np.where(BATLineUp.Optimizers.totalplayer==x)[0][0] for x in lineup['Name'].values]
		player = np.zeros(len(BATLineUp.Optimizers.totalplayer[:,0]))
		player[ind] = 1
		players.append(player)

	#Construct Order expected preformance for the TopPercent place
	G = []
	Values = []
	RSV = []
	Fraction = 1/(TopPercent/100)
	for i in range(numSims):
		Cov=GenerateCovarianceMtx(BATLineUp.Optimizers.totalplayer,'Data/DataBaseCrawler/TeamCovariance/')
		RS = np.random.multivariate_normal(BATLineUp.Optimizers.totalplayer[:,4].tolist(),Cov.todense())
		for i in range(len(RS)):
			if(BATLineUp.Optimizers.totalplayer[i,2]!='SP'):
				RS[i] = abs(RS[i])
		RealizedList = [sum(RS*x) for x in players]
		Slist = -np.sort(-np.array(RealizedList))
		value = Slist[int(len(Slist)/Fraction)]
		ind = np.where(RealizedList==value)[0][0]
		RSV.append(RS)
		G.append(players[ind]*RS)
		Values.append(value)

	Epoints = np.mean(Values)
	VPlayer = np.var(Values)

	#Model Covariance
	Gnp = np.array(G)
	RSVnp = np.array(RSV)
	Gr = np.mean(Gnp, axis=0)
	OutCov = []
	for i in range(len(Gr)):
		OutCov.append(np.cov(RSVnp[i,:],Gr)[0,1])

	return Epoints, VPlayer, OutCov