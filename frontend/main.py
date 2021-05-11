import sys
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app")
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app\\models")

from flask import Flask, session, render_template, request, url_for, redirect, Response
from flask_session import Session
from Universe import Universe
from Database import Database
import os
import pickle
import utils
import player_utils
import io
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

db = Database.getInstance()

app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/', methods = ['GET'])
def getHome():
    systems = db.cnx['soccersim']['systems'].find()
    return render_template('home.html', cssFiles = ['home.css'], systems = systems)

@app.route('/', methods = ['POST'])
def postHome():
    universeKey = request.form['universe_key']
    session['universeKey'] = universeKey
    session['universe'] = db.getUniverseGridFile(universeKey)
    return redirect(url_for('simulation'))

@app.route('/simulation')
def simulation():
    if 'universe' in session:
        universe = pickle.loads(session['universe'])
        league = universe.systems[0].leagues[0]

        ### Get standings
        leagueTable = league.getLeagueTable()
        leagueTableItems = list(leagueTable.items())
        leagueTableItems.sort(key = lambda x: (x[1]['Pts'], x[1]['GD']), reverse = True)

        # Get player performance
        playerPerformanceItems = league.getPerformanceIndices(sortBy = 'performanceIndex')

        ### Get results
        dates = {}
        for matchReport in league.matchReports:
            clubA, clubB = matchReport['clubs'].keys()
            match = list(matchReport['clubs'].values())[0]['match']
            scoreA, scoreB = match['goalsFor'], match['goalsAgainst']
            result = {
                'fixtureId': matchReport['fixture'],
                'homeClub': clubA,
                'awayClub': clubB,
                'homeScore': scoreA,
                'awayScore': scoreB
            }
            # strDate = matchReport['date'].strftime('%d %b')
            if matchReport['date'] not in dates:
                dates[matchReport['date']] = []
            dates[matchReport['date']].append(result)

        return render_template('simulation.html',
            cssFiles = ['rest_of_website.css'],
            jsFiles = ['script.js'],
            universeKey = session['universeKey'],
            leagueTableItems = leagueTableItems,
            playerPerformanceItems = playerPerformanceItems,
            dates = dates
            )
    return render_template('error.html')

@app.route('/simulation/default-iframe')
def default():
    return render_template('default_iframe.html', cssFiles = ['rest_of_website.css'])

@app.route('/simulation/player/<id>')
def player(id):
    if session['universe']:
        universe = pickle.loads(session['universe'])
        player = universe.playerController.getPlayerById(id)
        performanceIndices = player.club.league.getPerformanceIndices(sortBy = 'performanceIndex')[player]
    return render_template('player/player.html', cssFiles = ['rest_of_website.css', 'iframe.css'], jsFiles = ['iframe.js'], player = player, performanceIndices = performanceIndices)

@app.route('/simulation/player/<playerId>/radar')
def playerRadar(playerId):
    if session['universe']:
        universe = pickle.loads(session['universe'])
        player = universe.playerController.getPlayerById(playerId)
        fig = player_utils.showSkillDistribution(player, projection = True)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

@app.route('/simulation/player/<playerId>/form-graph')
def playerFormGraph(playerId):
    if session['universe']:
        universe = pickle.loads(session['universe'])
        player = universe.playerController.getPlayerById(playerId)
        fig = player_utils.showPlayerForm(player)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

@app.route('/simulation/fixture/<fixtureId>')
def fixture(fixtureId):
    if session['universe']:
        universe = pickle.loads(session['universe'])
        fixture = universe.getFixtureById(int(fixtureId))
        clubData = []
        for club, data in fixture.match.matchReport['clubs'].items():
            clubDatum = data
            clubDatum['name'] = club.name
            clubData.append(clubDatum)
        homeClubData, awayClubData = clubData
        def get_reverse_fixture(fixture):
            for otherFixture in fixture.tournament.fixtures:
                if fixture.clubX == otherFixture.clubY and fixture.clubY == otherFixture.clubX:
                    return otherFixture

        positions = ['CF', 'WF', 'COM', 'WM', 'CM', 'CDM', 'WB', 'FB', 'CB']
        for clubData in [homeClubData, awayClubData]:
            reorderedPlayers = sorted(clubData['players'].items(), key = lambda x: positions.index(x[1]['position']))
            clubData['players'] = {k: v for k, v in reorderedPlayers}
            for player, data in clubData['players'].items():
                clubData['players'][player]['extraData']['selectRating'] = '{:.2f}'.format(data['extraData']['selectRating'])
                clubData['players'][player]['performanceIndex'] = '{:.2f}'.format(data['performanceIndex'])

        reverseFixtureData = {}
        reverseFixture = get_reverse_fixture(fixture)
        reverseFixtureData['fixtureId'] = reverseFixture.id
        reverseFixtureData['homeTeam'] = reverseFixture.clubX.name
        reverseFixtureData['homeGoals'] = reverseFixture.match.matchReport['clubs'][reverseFixture.clubX]['match']['goalsFor']
        reverseFixtureData['awayTeam'] = reverseFixture.clubY.name
        reverseFixtureData['awayGoals'] = reverseFixture.match.matchReport['clubs'][reverseFixture.clubY]['match']['goalsFor']

        recentResults = {}
        preMatchLeagueTables = {'name': 'Pre-match', 'data': {}}
        postMatchLeagueTables = {'name': 'Post-match', 'data': {}}
        for club in fixture.match.matchReport['clubs']:
            recentResults[club] = {
                'points': 0,
                'results': []
            }
            fixturesInvolvingClub = list(filter(lambda x: club in x.clubs, fixture.tournament.fixtures))
            fixtureIndex = fixturesInvolvingClub.index(fixture)
            
            for i, leagueTables in enumerate([preMatchLeagueTables, postMatchLeagueTables]):
                leagueTable = fixture.tournament.getLeagueTable(fixtureIndex + i) if fixtureIndex > 0 else None
                if leagueTable:
                    leagueTableItems = list(leagueTable.items())
                    leagueTableItems.sort(key = lambda x: (x[1]['Pts'], x[1]['GD']), reverse = True)
                    for j, leagueTableItem in enumerate(leagueTableItems):
                        leagueTableItem[1]['#'] = j + 1
                        if leagueTableItem[0] == club:
                            leagueTableItem[1]['this'] = True
                            tableIndex = j
                    if tableIndex < 1:
                        startTableIndex = 0
                        endTableIndex = 3
                    elif tableIndex > (len(leagueTableItems) - 2):
                        startTableIndex = len(leagueTableItems) - 3
                        endTableIndex = len(leagueTableItems)
                    else:
                        startTableIndex = tableIndex - 1
                        endTableIndex = tableIndex + 2
                    leagueTable = leagueTableItems[startTableIndex:endTableIndex]
                    leagueTables['data'][club] = leagueTable

            ### This bit is almost a duplicate of above, combine
            # postMatchLeagueTable = fixture.tournament.getLeagueTable(fixtureIndex + 1)
            # leagueTableItems = list(postMatchLeagueTable.items())
            # leagueTableItems.sort(key = lambda x: (x[1]['Pts'], x[1]['GD']), reverse = True)
            # for i, leagueTableItem in enumerate(leagueTableItems):
            #     if leagueTableItem[0] == club:
            #         tableIndex = i
            #         break
            # if tableIndex < 2:
            #     startTableIndex = 0
            #     endTableIndex = 5
            # elif tableIndex > (len(leagueTableItems) - 2):
            #     startTableIndex = len(leagueTableItems) - 5
            #     endTableIndex = len(leagueTableItems)
            # else:
            #     startTableIndex = tableIndex - 2
            #     endTableIndex = tableIndex + 3
            # postMatchLeagueTable = leagueTableItems[startTableIndex:endTableIndex]
            # postMatchLeagueTables[club] = postMatchLeagueTable

            fixturesOfInterest = fixturesInvolvingClub[fixtureIndex - min(fixtureIndex, 6):fixtureIndex]
            for fixtureOfInterest in fixturesOfInterest:
                result = 'D' if 'winner' not in fixtureOfInterest.match.matchReport else 'W' if fixtureOfInterest.match.matchReport['winner'] == club else 'L'
                recentResults[club]['points'] += 3 if result == 'W' else 1 if result == 'D' else 0
                score = '{} {} - {} {}'.format(
                    fixtureOfInterest.clubX.name,
                    fixtureOfInterest.match.matchReport['clubs'][fixtureOfInterest.clubX]['match']['goalsFor'],
                    fixtureOfInterest.match.matchReport['clubs'][fixtureOfInterest.clubY]['match']['goalsFor'],
                    fixtureOfInterest.clubY.name,
                )
                fixtureId = fixtureOfInterest.id
                recentResults[club]['results'].append({
                    'result': result,
                    'score': score,
                    'fixtureId': fixtureId
                })

    return render_template(
        'fixture/fixture.html',
        cssFiles = ['rest_of_website.css', 'iframe.css'],
        jsFiles = ['fixture.js', 'iframe.js'],
        fixture = fixture,
        homeClubData = homeClubData,
        awayClubData = awayClubData,
        reverseFixture = reverseFixtureData,
        recentResults = recentResults,
        preMatchLeagueTables = preMatchLeagueTables,
        postMatchLeagueTables = postMatchLeagueTables
    )

### For versioning CSS to prevent browser cacheing
@app.context_processor
def inject_dict_for_all_templates():
    randomString = utils.generateRandomDigits(5)
    return {'randomString': randomString}

### Dev methods for convenience
@app.route('/clear', methods = ['GET'])
def clearSession():
    session.clear()
    return redirect(url_for('getHome'))

if __name__ == '__main__':
    app.run(debug = True)