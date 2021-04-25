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
    return render_template('home.html', cssFile = 'home.css', systems = systems)

@app.route('/', methods = ['POST'])
def postHome():
    universeKey = request.form['universe_key']
    session['universeKey'] = universeKey
    session['universe'] = db.getUniverse(universeKey)
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
            cssFile = 'rest_of_website.css',
            universeKey = session['universeKey'],
            leagueTableItems = leagueTableItems,
            playerPerformanceItems = playerPerformanceItems,
            dates = dates
            )
    return render_template('error.html')

@app.route('/simulation/default-iframe')
def default():
    return render_template('default_iframe.html', cssFile = 'rest_of_website.css')

@app.route('/simulation/player/<id>')
def player(id):
    if session['universe']:
        universe = pickle.loads(session['universe'])
        player = universe.playerController.getPlayerById(id)
    return render_template('player.html', cssFile = 'rest_of_website.css', player = player)

@app.route('/simulation/player/<id>/radar')
def playerRadar(id):
    if session['universe']:
        universe = pickle.loads(session['universe'])
        player = universe.playerController.getPlayerById(id)
        fig = player_utils.showSkillDistribution(player, projection = True)
        output = io.BytesIO()
        FigureCanvas(fig).print_png(output)
        return Response(output.getvalue(), mimetype='image/png')

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