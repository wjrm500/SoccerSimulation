import io
import json
import os
import pickle
from datetime import timedelta
from io import BytesIO

import matplotlib.pyplot as plt
import redis
from flask import (
    Flask,
    Response,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_mobility import Mobility
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from rq import Queue

import ss.club_utils as club_utils
import ss.player_utils as player_utils
import ss.utils as utils
from flask_session import Session
from ss.config import playerConfig
from ss.models.Database import Database
from ss.simulate import simulate
from worker import conn

db = Database.getInstance()  ### MongoDB
q = Queue(connection=conn)
r = redis.Redis(host="redis", port=6379)
TTL_SECONDS = 3600  # store simulation data for one hour

template_folder = os.path.abspath("frontend/templates")
static_folder = os.path.abspath("frontend/static")
app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
app.secret_key = os.urandom(12).hex()
app.config["SESSION_TYPE"] = "filesystem"
Session(app)
Mobility(app)


def getUniverse():
    if "universe" not in g:
        active_key = session.get("activeUniverseKey")
        if not active_key:
            abort(400, description="Simulation not set")
        universe_data = db.getUniverseGridFile(active_key)
        if universe_data is None:
            abort(404, description="Simulation data not found")
        g.universe = pickle.loads(universe_data)
    return g.universe


def getSearchGameweek(league):
    gameweek = request.args.get("gameweek") or ""
    lastGameweek = (len(league.clubs) - 1) * 2
    searchGameweek = lastGameweek
    if gameweek.isnumeric():
        gameweek = int(gameweek)
        if gameweek <= lastGameweek:
            searchGameweek = gameweek
    return searchGameweek


def showSimulation():
    activeUniverseKey = session["activeUniverseKey"]
    universe = getUniverse()
    league = universe.systems[0].leagues[0]

    searchGameweek = getSearchGameweek(league)
    ### Get standings
    leagueTable = league.getLeagueTable(searchGameweek)
    leagueTableItems = list(leagueTable.items())
    leagueTableItems.sort(key=lambda x: (x[1]["Pts"], x[1]["GD"]), reverse=True)

    # Get player performance
    playerPerformanceItems = league.getPerformanceIndices(
        sortBy="performanceIndex", gameweek=searchGameweek
    )

    ### Get results
    dates = {}
    for matchReport in league.matchReports:
        if matchReport["gameweek"] > searchGameweek:
            break
        clubs = list(matchReport["clubs"].keys())
        if len(clubs) >= 2:
            clubA, clubB = clubs[0], clubs[1]
        else:
            clubA = clubs[0]
            clubB = None
        match = list(matchReport["clubs"].values())[0]["match"]
        scoreA, scoreB = match["goalsFor"], match["goalsAgainst"]
        result = {
            "fixtureId": matchReport["fixtureId"],
            "homeClub": clubA,
            "awayClub": clubB,
            "homeScore": scoreA,
            "awayScore": scoreB,
        }
        if matchReport["date"] not in dates:
            dates[matchReport["date"]] = []
        dates[matchReport["date"]].append(result)

    if request.MOBILE:
        return render_template(
            "mobile/simulation.html",
            cssFiles=["rest_of_website.css", "mobile.css"],
            jsFiles=["mobile.js"],
            universeKey=activeUniverseKey,
            leagueTableItems=leagueTableItems,
            playerPerformanceItems=playerPerformanceItems,
            dates=dates,
        )

    return render_template(
        "desktop/simulation.html",
        cssFiles=["rest_of_website.css"],
        jsFiles=["script.js"],
        universeKey=activeUniverseKey,
        leagueTableItems=leagueTableItems,
        playerPerformanceItems=playerPerformanceItems,
        dates=dates,
    )


@app.route("/", methods=["GET"])
def getHome():
    return render_template("desktop/home-initial.html", cssFiles=["home.css"], jsFiles=["home.js"])


@app.route("/", methods=["POST"])
def postHome():
    universeKey = request.form["universe_key"]
    url = url_for("simulation", universeKey=universeKey)
    return redirect(url)


@app.route("/new-simulation", methods=["GET"])
def getNewSimulation():
    systems = db.cnx["soccersim"]["systems"].find().sort("system_name", 1)
    return render_template(
        "desktop/home-new.html",
        cssFiles=["home.css"],
        jsFiles=["home.js"],
        systems=systems,
    )


@app.route("/new-simulation", methods=["POST"])
def postNewSimulation():
    systemId = int(request.form["system"])
    customConfig = {
        "numLeaguesPerSystem": None,
        "numClubsPerLeague": int(request.form["num-clubs"]),
        "numPlayersPerClub": int(request.form["num-players-per-club"]),
        "customClubs": json.loads(request.form["custom-clubs"]),
    }
    universeKey = utils.makeUniverseKey()
    r.set("simulation_progress_" + universeKey, 0)
    q.enqueue(simulate, customConfig, systemId, universeKey, job_timeout=3600)
    return render_template(
        "desktop/waiting.html",
        universeKey=universeKey,
        cssFiles=["home.css"],
        jsFiles=["waiting.js"],
    )


@app.route("/existing-simulation", methods=["GET"])
def getExistingSimulation():
    return render_template("desktop/home-existing.html", cssFiles=["home.css"], jsFiles=["home.js"])


@app.route("/existing-simulation", methods=["POST"])
def postExistingSimulation():
    error = "ERROR: "
    existingHow = request.form.get("existing-how")
    if existingHow == "remote":
        universeKey = request.form.get("universe-key")
        if db.universeKeyExists(universeKey):
            url = url_for("simulation", universeKey=universeKey)
            return redirect(url)
        error += f"Universe Key {universeKey} does not exist"
    elif existingHow == "local":
        file = request.files.get("upload-file")
        universe = file.read()
        new_key = utils.makeUniverseKey(9)
        session["activeUniverseKey"] = new_key
        r.setex("simulation_" + new_key, TTL_SECONDS, universe)
        try:
            return showSimulation()
        except Exception as e:
            error += "Invalid file upload: " + str(e)
    return render_template(
        "desktop/home-existing.html",
        cssFiles=["home.css"],
        jsFiles=["home.js"],
        error=error,
    )


@app.route("/simulation/check-progress/<universeKey>", methods=["GET"])
def checkSimulationProgress(universeKey):
    redisKey = "simulation_progress_" + universeKey
    if r.exists(redisKey):
        return r.get(redisKey).decode("utf-8")


@app.route("/simulation/check-universe-key-exists-in-database/<universeKey>", methods=["GET"])
def checkUniverseKeyExistsInDatabase(universeKey):
    universe = db.getUniverseGridFile(universeKey)
    if universe:
        session["activeUniverseKey"] = universeKey
        r.setex("simulation_" + universeKey, TTL_SECONDS, universe)
        return json.dumps(True)
    return json.dumps(False)


@app.route("/simulation/store-email", methods=["POST"])
def storeEmail():
    email_input = request.form.get("email_input")
    universe_key = request.form.get("universe_key")
    r.set("email_" + universe_key, email_input)
    return jsonify("success")


@app.route("/simulation/<universeKey>")
def simulation(universeKey):
    session["activeUniverseKey"] = universeKey
    universe_data = db.getUniverseGridFile(universeKey)
    if universe_data is None:
        return "Universe not found", 404
    return showSimulation()


@app.route("/download/<universeKey>")
def download(universeKey):
    universe_data = db.getUniverseGridFile(universeKey)
    if universe_data is None:
        return "Simulation data not found", 404
    attachmentFilename = "universe_" + universeKey
    return send_file(BytesIO(universe_data), download_name=attachmentFilename, as_attachment=True)


@app.route("/simulation/default-iframe")
def default():
    return render_template("desktop/default_iframe.html", cssFiles=["rest_of_website.css"])


@app.route("/simulation/player/<id>")
def player(id):
    universe = getUniverse()
    searchGameweek = getSearchGameweek(universe.systems[0].leagues[0])
    player = universe.playerController.getPlayerById(id)
    performanceIndices = player.club.league.getPerformanceIndices(
        sortBy="performanceIndex", gameweek=searchGameweek
    )[player]
    maxDate = None
    if request.args.get("gameweek"):
        maxDate = player.club.league.gameweekDates[searchGameweek]
    injuries = []
    for injury in player.injuries:
        startDate = injury[0]
        if maxDate is not None and startDate > maxDate:
            continue
        injuryLength = injury[1]
        endDate = startDate + timedelta(int(injuryLength))
        if maxDate is not None and endDate > maxDate:
            injuryText = "Since {}".format(startDate.strftime("%d %b"))
        else:
            injuryText = "Between {} and {} ({} days)".format(
                startDate.strftime("%d %b"), endDate.strftime("%d %b"), injuryLength
            )
        injuries.append(injuryText)
    performanceIndices["injuries"] = injuries
    yR = [val["rating"] for val in list(player.ratings.values())]
    yPR = [val["peakRating"] for val in list(player.ratings.values())]
    playerDevelopment = {
        "rating": {
            "start": yR[0],
            "end": player.ratings[maxDate]["rating"] if request.args.get("gameweek") else yR[-1],
        },
        "peakRating": {
            "start": yPR[0],
            "end": player.ratings[maxDate]["peakRating"]
            if request.args.get("gameweek")
            else player.peakRating,
        },
    }
    playerBestPosition = (
        player.getBestPosition(player.getSkillDistribution(player.getAgeOnDate(maxDate)))
        if request.args.get("gameweek")
        else player.getBestPosition()
    )
    return render_template(
        "desktop/player/player.html",
        cssFiles=["rest_of_website.css", "iframe.css"],
        jsFiles=["iframe.js", "player.js"],
        player=player,
        playerBestPosition=playerBestPosition,
        playerRating=player.ratings[maxDate]["rating"]
        if request.args.get("gameweek")
        else player.getRating(),
        playerPeakRating=player.ratings[maxDate]["peakRating"]
        if request.args.get("gameweek")
        else player.peakRating,
        playerAge=player.getAgeOnDate(maxDate, 2)
        if request.args.get("gameweek")
        else player.getAge(2),
        playerReports=player.getPlayerReports(searchGameweek),
        performanceIndices=performanceIndices,
        playerDevelopment=playerDevelopment,
    )


@app.route("/simulation/player/<playerId>/radar")
def playerRadar(playerId):
    universe = getUniverse()
    player = universe.playerController.getPlayerById(playerId)
    league = universe.systems[0].leagues[0]
    searchGameweek = getSearchGameweek(league)
    if request.args.get("gameweek"):
        maxDate = league.gameweekDates[searchGameweek]
    else:
        maxDate = None
    date = maxDate if request.args.get("gameweek") else None
    fig = player_utils.showSkillDistribution(player, date=date, projection=True)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")


@app.route("/simulation/player/<playerId>/form-graph")
def playerFormGraph(playerId):
    universe = getUniverse()
    player = universe.playerController.getPlayerById(playerId)
    fig = player_utils.showPlayerForm(player)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")


@app.route("/simulation/player/<playerId>/development-graph")
def playerDevelopmentGraph(playerId):
    universe = getUniverse()
    league = universe.systems[0].leagues[0]
    date = None
    if request.args.get("gameweek"):
        searchGameweek = getSearchGameweek(league)
        maxDate = league.gameweekDates[searchGameweek]
        date = maxDate
    player = universe.playerController.getPlayerById(playerId)
    fig = player_utils.showPlayerDevelopment(player, date=date)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")


@app.route("/simulation/fixture/<fixtureId>")
def fixture(fixtureId):
    universe = getUniverse()
    fixture = universe.getFixtureById(int(fixtureId))
    clubData = []
    for club, data in fixture.match.matchReport["clubs"].items():
        clubDatum = data
        clubDatum["id"] = club.id
        clubDatum["name"] = club.name
        clubData.append(clubDatum)
    homeClubData, awayClubData = clubData

    def get_reverse_fixture(fixture):
        for otherFixture in fixture.tournament.fixtures:
            if fixture.clubX == otherFixture.clubY and fixture.clubY == otherFixture.clubX:
                return otherFixture

    positions = ["CF", "WF", "COM", "WM", "CM", "CDM", "WB", "FB", "CB"]
    for clubData in [homeClubData, awayClubData]:
        reorderedPlayers = sorted(
            clubData["players"].items(), key=lambda x: positions.index(x[1]["position"])
        )
        clubData["players"] = dict(reorderedPlayers)
        for player, data in clubData["players"].items():
            preMatchForm = data["preMatchForm"]
            prefix = "+" if preMatchForm > 0 else "±" if preMatchForm == 0 else ""
            preMatchFormText = f"{prefix}{preMatchForm:.2f}"
            clubData["players"][player]["extraData"]["preMatchForm"] = preMatchFormText
            clubData["players"][player]["extraData"]["selectRating"] = "{:.2f}".format(
                data["extraData"]["selectRating"]
            )
            clubData["players"][player]["performanceIndex"] = "{:.2f}".format(
                data["performanceIndex"]
            )

    reverseFixtureData = {}
    reverseFixture = get_reverse_fixture(fixture)
    reverseFixtureData["fixtureId"] = reverseFixture.id
    reverseFixtureData["homeTeam"] = reverseFixture.clubX.name
    reverseFixtureData["homeGoals"] = reverseFixture.match.matchReport["clubs"][
        reverseFixture.clubX
    ]["match"]["goalsFor"]
    reverseFixtureData["awayTeam"] = reverseFixture.clubY.name
    reverseFixtureData["awayGoals"] = reverseFixture.match.matchReport["clubs"][
        reverseFixture.clubY
    ]["match"]["goalsFor"]

    recentResults = {}
    preMatchLeagueTables = {"name": "Pre-match", "data": {}}
    postMatchLeagueTables = {"name": "Post-match", "data": {}}
    for club in fixture.match.matchReport["clubs"]:
        recentResults[club] = {"points": 0, "results": []}
        fixturesInvolvingClub = list(filter(lambda x: club in x.clubs, fixture.tournament.fixtures))
        fixtureIndex = fixturesInvolvingClub.index(fixture)
        for i, leagueTables in enumerate([preMatchLeagueTables, postMatchLeagueTables]):
            leagueTable = (
                fixture.tournament.getLeagueTable(fixtureIndex + i) if fixtureIndex > 0 else None
            )
            if leagueTable:
                leagueTableItems = list(leagueTable.items())
                leagueTableItems.sort(key=lambda x: (x[1]["Pts"], x[1]["GD"]), reverse=True)
                for j, leagueTableItem in enumerate(leagueTableItems):
                    leagueTableItem[1]["#"] = j + 1
                    if leagueTableItem[0] == club:
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
                leagueTables["data"][club] = leagueTable

        fixturesOfInterest = fixturesInvolvingClub[
            fixtureIndex - min(fixtureIndex, 6) : fixtureIndex
        ]
        for fixtureOfInterest in fixturesOfInterest:
            result = (
                "D"
                if "winner" not in fixtureOfInterest.match.matchReport
                else "W"
                if fixtureOfInterest.match.matchReport["winner"] == club
                else "L"
            )
            recentResults[club]["points"] += 3 if result == "W" else 1 if result == "D" else 0
            score = "{} {} - {} {}".format(
                fixtureOfInterest.clubX.name,
                fixtureOfInterest.match.matchReport["clubs"][fixtureOfInterest.clubX]["match"][
                    "goalsFor"
                ],
                fixtureOfInterest.match.matchReport["clubs"][fixtureOfInterest.clubY]["match"][
                    "goalsFor"
                ],
                fixtureOfInterest.clubY.name,
            )
            fixtureId = fixtureOfInterest.id
            recentResults[club]["results"].append(
                {"result": result, "score": score, "fixtureId": fixtureId}
            )

    return render_template(
        "desktop/fixture/fixture.html",
        cssFiles=["rest_of_website.css", "iframe.css"],
        jsFiles=["fixture.js", "iframe.js"],
        fixture=fixture,
        homeClubData=homeClubData,
        awayClubData=awayClubData,
        reverseFixture=reverseFixtureData,
        recentResults=recentResults,
        preMatchLeagueTables=preMatchLeagueTables,
        postMatchLeagueTables=postMatchLeagueTables,
        numClubs=len(universe.systems[0].leagues[0].clubs),
    )


@app.route("/simulation/club/<clubId>")
def club(clubId):
    universe = getUniverse()
    club = universe.getClubById(clubId)
    team = club.selectTeam(test=True)
    selection = team.selection
    formation = team.formation
    averageSelectRating = sum([select.rating for select in selection]) / 10
    players = json.dumps(
        [
            {
                "adjustedRating": (select.rating - averageSelectRating) / averageSelectRating,
                "id": select.player.id,
                "name": select.player.getClubSpecificName(),
                "position": select.position,
                "rating": select.rating,
            }
            for select in selection
        ]
    )
    searchGameweek = getSearchGameweek(universe.systems[0].leagues[0])
    playerPerformanceItems = club.league.getPerformanceIndices(
        sortBy="performanceIndex", gameweek=searchGameweek, clubs=club
    )

    results = []
    for matchReport in club.getMatchReports(searchGameweek):
        atHome = club == list(matchReport["clubs"].keys())[0]
        oppClub = [x for x in list(matchReport["clubs"].keys()) if x != club][0]
        clubScore = matchReport["clubs"][club]["match"]["goalsFor"]
        oppClubScore = matchReport["clubs"][oppClub]["match"]["goalsFor"]
        result = {
            "atHome": atHome,
            "fixtureId": matchReport["fixtureId"],
            "gameweek": matchReport["gameweek"],
            "club": club,
            "oppClub": oppClub,
            "clubScore": clubScore,
            "oppClubScore": oppClubScore,
            "result": "win"
            if clubScore > oppClubScore
            else "loss"
            if oppClubScore > clubScore
            else "draw",
        }
        results.append(result)
    return render_template(
        "desktop/club/club.html",
        cssFiles=["rest_of_website.css", "iframe.css"],
        jsFiles=["club.js", "iframe.js"],
        club=club,
        formation=formation,
        players=players,
        playerPerformanceItems=playerPerformanceItems,
        results=results,
    )


@app.route("/simulation/player-performance")
def playerPerformance():
    universe = getUniverse()
    league = universe.systems[0].leagues[0]
    searchGameweek = getSearchGameweek(league)
    playerPerformanceItems = league.getPerformanceIndices(
        sortBy="performanceIndex", gameweek=searchGameweek
    )
    filterClubs = sorted(
        [{"id": club.id, "name": club.name} for club in league.clubs],
        key=lambda x: x["name"],
    )
    filterPositions = list(playerConfig["positions"].keys())
    return render_template(
        "desktop/player_performance_proper.html",
        cssFiles=["rest_of_website.css", "iframe.css"],
        jsFiles=["iframe.js", "player_performance.js"],
        filterClubs=filterClubs,
        filterPositions=filterPositions,
        playerPerformanceItems=playerPerformanceItems,
    )


@app.route("/simulation/club/<clubId>/position-graph")
def clubPositionGraph(clubId):
    universe = getUniverse()
    club = universe.getClubById(clubId)
    searchGameweek = getSearchGameweek(universe.systems[0].leagues[0])
    fig = club_utils.showClubPositions(club, gameweek=searchGameweek)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)
    plt.close(fig)
    return Response(output.getvalue(), mimetype="image/png")


@app.route("/about", methods=["GET"])
def about():
    if request.MOBILE:
        return render_template("mobile/about.html", cssFiles=["rest_of_website.css", "mobile.css"])
    return render_template(
        "desktop/about.html", cssFiles=["rest_of_website.css"], jsFiles=["script.js"]
    )


@app.route("/contact", methods=["GET"])
def contact():
    if request.MOBILE:
        return render_template(
            "mobile/contact.html", cssFiles=["rest_of_website.css", "mobile.css"]
        )
    return render_template(
        "desktop/contact.html", cssFiles=["rest_of_website.css"], jsFiles=["script.js"]
    )


@app.context_processor
def inject_dict_for_all_templates():
    randomString = utils.generateRandomDigits(5)
    return {"randomString": randomString}


### Dev methods for convenience
@app.route("/clear", methods=["GET"])
def clearSession():
    session.clear()
    url = url_for("getHome")
    return redirect(url)
