# DFSSummerProject
This project was done in the summer of 2018. I have since taken a class in Software Engineering and will need to refactor the code base.  I made some silly mistakes that would need to be corrected.

If you are wanting to play with my code you need Gurobi Optimzation package.
The webscraper I wrote grabs the current date for line ups, since there is no game data past September 5th I recommend to see it run you pick Sept5 for the date, and set the know flag to false. I switched the predictions I was using near the end, so this will stop any conflicts.

I recommend running the DraftKingsPredictionsQuad since it solves the BIP problem, and if you are wanting to see how I modeled the population you can check out the files in LineUpGenPopModel.

The solver to find the best strategy followed this paper very closely: http://www.sloansportsconference.com/wp-content/uploads/2018/02/1001.pdf

To generate my own predictions I used a lot of sabermetic papers, blogs, and my own ideas. I got a lot of hints on where to look for building predictors here: https://rotogrinders.com/pages/how-the-bat-works-1242325

Most of the data scraped was from FanGraphs and Retosheets.  If you are wanting to use my Gamelogs or data for anything please referance them.
