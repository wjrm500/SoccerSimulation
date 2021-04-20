import sys
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app")
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app\\models")

from flask import Flask, session, render_template, request, url_for, redirect
from flask_session import Session
from Universe import Universe
from Database import Database
import os
import pickle
import utils

db = Database.getInstance()

app = Flask(__name__)
app.secret_key = os.urandom(12).hex()
app.config['SESSION_TYPE'] = 'filesystem'
Session(app)

@app.route('/', methods = ['GET'])
def getHome():
    systems = db.cnx['soccersim']['systems'].find()
    return render_template('home.html', systems = systems)

@app.route('/', methods = ['POST'])
def postHome():
    universeKey = request.form['universe_key']
    if 'universe' not in session:
        session['universe'] = db.getUniverse(universeKey)
    return redirect(url_for('simulation'))

@app.route('/simulation')
def simulation():
    if 'universe' in session:
        universe = pickle.loads(session['universe'])
        leagueTable = universe.systems[0].leagues[0].getLeagueTable()
        leagueTableItems = list(leagueTable.items())
        leagueTableItems.sort(key = lambda x: (x[1]['Pts'], x[1]['GD']), reverse = True)
        return render_template('simulation.html', leagueTableItems = leagueTableItems)
    return render_template('error.html')

@app.route('/player/<id>')
def player(id):
    if session.universe:
        player = session.universe.getPlayerById(id)
    return player.name

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