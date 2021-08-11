from .. import goal_probability, utils
import numpy as np

class PlayerReportEngine:
    def __init__(self, match):
        self.match = match
        self.manOfTheMatch = None
    
    def generatePlayerReports(self, report):
        meanFitness = np.mean([select.player.skillValues['fitness'] for club in self.match.clubs for select in report['clubs'][club]['team'].selection])
        for club in self.match.clubs:
            team = report['clubs'][club]['team']
            report['clubs'][club]['players'] = {}
            for select in team.selection:
                player = select.player
                report['clubs'][club]['players'][player] = self.getPlayerReport(club, team, select, meanFitness)

        ### Tag man of the match
        manOfTheMatch = self.manOfTheMatch['player']
        for club in self.match.clubs:
            team = report['clubs'][club]['team']
            for select in team.selection:
                player = select.player
                report['clubs'][club]['players'][player]['manOfTheMatch'] = player == manOfTheMatch

    def getPlayerReport(self, club, team, select, meanFitness):
        player = select.player
        position = select.position
        playerReport = {}
        playerGoalLikelihood = team.goalFactors[player]
        playerAssistLikelihood = team.assistFactors[player]
        playerReport['fixtureId'] = self.match.fixture.id
        playerReport['homeAway'] = 'H' if self.match.clubX == player.club else 'A'
        playerReport['tournament'] = self.match.tournament.tournament if type(self.match.tournament).__name__ == 'Group' else self.match.tournament
        playerReport['date'] = self.match.date
        playerReport['gameweek'] = self.match.fixture.gameweek
        playerReport['position'] = position
        playerReport['preMatchFatigue'] = player.fatigue
        playerReport['preMatchForm'] = player.form
        
        club = player.club
        oppositionClub = self.match.getOppositionClub(club)
        clubReport = self.match.matchReport['clubs'][club] ### TODO
        oppositionClubReport = self.match.matchReport['clubs'][oppositionClub]
        goals = clubReport['match']['goals']
        playerReport['goals'] = sum([1 for goal in goals if goal['scorer'] == player]) if goals is not None else 0
        playerReport['assists'] = sum([1 for goal in goals if goal['assister'] == player]) if goals is not None else 0

        playerReport['oppositionClub'] = oppositionClub

        ### Get player performance index

        select = clubReport['team'].getSelectFromPlayer(player)
        selectRating = clubReport['team'].getSelectRating(select)
        oppositionTeamRating = oppositionClubReport['team'].averageRating
        ratingAdvantage = selectRating - oppositionTeamRating
        x = ratingAdvantage
        baseRating = ((1 / (1 + np.power(np.e, (-x / 12.5)))) + 0.5) * 5
        modulatedBaseRating = utils.limitedRandNorm({'mu': baseRating, 'sg': 0.5, 'mn': 2.5, 'mx': 7.5})

        offensiveContribution = clubReport['team'].selectionOffensiveContributions[select]
        defensiveContribution = clubReport['team'].selectionDefensiveContributions[select]
        teamPredictedGoalsFor = utils.limitValue(goal_probability.goalProbability[int(clubReport['potential'])]['mu'], mn = 0) ### What if team predicted goals for was based on the individual's potential
        teamActualGoalsFor = clubReport['match']['goalsFor']
        teamOffensiveOutperformance = teamActualGoalsFor - teamPredictedGoalsFor
        teamPredictedGoalsAgainst = utils.limitValue(goal_probability.goalProbability[int(oppositionClubReport['potential'])]['mu'], mn = 0)
        teamActualGoalsAgainst = oppositionClubReport['match']['goalsFor']
        teamDefensiveOutperformance = teamPredictedGoalsAgainst - teamActualGoalsAgainst
        offensiveBoost = utils.limitValue(offensiveContribution * teamOffensiveOutperformance * 5, mn = -1.5, mx = 1.5)
        defensiveBoost = utils.limitValue(defensiveContribution * teamDefensiveOutperformance * 5, mn = -1.5, mx = 1.5)

        goalDifference = abs(clubReport['match']['goalsFor'] - oppositionClubReport['match']['goalsFor'])
        goalsScored = clubReport['match']['goalsFor'] + oppositionClubReport['match']['goalsFor']
        ratingBoostForGoal, ratingBoostForAssist = self.getRatingBoostsForGoalsAndAssists(goalDifference, goalsScored)

        playerPredictedGoals = teamPredictedGoalsFor * playerGoalLikelihood
        goalNegative = playerPredictedGoals * ratingBoostForGoal / 5 ### Dividing by 5 intended to boost goal involvements and help compensate for the disproportionate effects of any potential 10-cap
        goalPositive = playerReport['goals'] * ratingBoostForGoal

        playerPredictedAssists = teamPredictedGoalsFor * 0.9 * playerAssistLikelihood
        assistNegative = playerPredictedAssists * ratingBoostForAssist  / 5
        assistPositive = playerReport['assists'] * ratingBoostForAssist

        performanceIndex = utils.limitValue(
            modulatedBaseRating + offensiveBoost + defensiveBoost - goalNegative + goalPositive - assistNegative + assistPositive,
            mn = 0,
            mx = 10
        )
        playerReport['performanceIndex'] = performanceIndex

        if self.manOfTheMatch is None or performanceIndex > self.manOfTheMatch['performanceIndex']:
            self.manOfTheMatch = {'player': player, 'performanceIndex': performanceIndex}

        ### Handle fatigue

        fitnessFromMean = utils.limitValue(player.skillValues['fitness'] - meanFitness, mn = -35, mx = 35)
        a = np.power(abs(fitnessFromMean) / 10, 2) / 25
        b = np.power(a, 1.5)
        if fitnessFromMean > 0:
            mu = 0.25 - a + b
        else:
            mu = 0.25 + a - b
        fatigueIncrease = utils.limitedRandNorm({'mu': mu, 'sg': 0.05, 'mn': 0.05, 'mx': 0.45})
        playerReport['fatigueIncrease'] = fatigueIncrease
        
        ### Handle form

        outperformance = playerReport['performanceIndex'] - baseRating
        ungravitatedMatchForm = outperformance / 5
        gravity = player.form / 10
        gravitatedMatchForm = ungravitatedMatchForm - gravity
        playerReport['ungravitatedMatchForm'] = ungravitatedMatchForm
        playerReport['gravitatedMatchForm'] = gravitatedMatchForm

        ### Add extra data

        playerReport['extraData'] = {}
        playerReport['extraData']['selectRating'] = selectRating
        playerReport['extraData']['oppositionTeamRating'] = oppositionTeamRating
        playerReport['extraData']['baseRating'] = baseRating
        playerReport['extraData']['modulatedBaseRating'] = modulatedBaseRating
        playerReport['extraData']['offensiveContribution'] = offensiveContribution
        playerReport['extraData']['defensiveContribution'] = defensiveContribution
        playerReport['extraData']['teamPredictedGoalsFor'] = teamPredictedGoalsFor
        playerReport['extraData']['teamActualGoalsFor'] = teamActualGoalsFor
        playerReport['extraData']['teamOffensiveOutperformance'] = teamOffensiveOutperformance
        playerReport['extraData']['teamPredictedGoalsAgainst'] = teamPredictedGoalsAgainst
        playerReport['extraData']['teamActualGoalsAgainst'] = teamActualGoalsAgainst
        playerReport['extraData']['teamDefensiveOutperformance'] = teamDefensiveOutperformance
        playerReport['extraData']['offensiveBoost'] = offensiveBoost
        playerReport['extraData']['defensiveBoost'] = defensiveBoost
        playerReport['extraData']['predictedGoals'] = playerPredictedGoals
        playerReport['extraData']['goalNegative'] = goalNegative
        playerReport['extraData']['goalPositive'] = goalPositive
        playerReport['extraData']['predictedAssists'] = playerPredictedAssists
        playerReport['extraData']['assistNegative'] = assistNegative
        playerReport['extraData']['assistPositive'] = assistPositive

        return playerReport
    
    def getRatingBoostsForGoalsAndAssists(self, goalDifference, goalsScored):
        goalDifferenceComponentOfRatingBoostForGoal = 1.5 if goalDifference == 0 else 2.5 - np.power(goalDifference, (1 / 4))
        goalsScoredComponentOfRatingBoostForGoal = 1.5 if goalsScored == 0 else 1.5 - (goalsScored - 1) * (3 / 40)
        ratingBoostForGoal = ((goalDifferenceComponentOfRatingBoostForGoal * 2) + goalsScoredComponentOfRatingBoostForGoal) / 3
        ratingBoostForAssist = ratingBoostForGoal * 0.75
        return [ratingBoostForGoal, ratingBoostForAssist]