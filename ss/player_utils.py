import math

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import dates as mdates


def showPredictedRatings(player):
    ageList, predictedRatingList = [], []
    for age in range(15, 40):
        ageList.append(age)
        predictedRating = player.calculateRating(age)
        predictedRatingList.append(predictedRating)
    ageArray = np.array(ageList)
    predictedRatingArray = np.array(predictedRatingList)
    x, y = ageArray, predictedRatingArray
    plt.plot(x, y)
    for xy in zip(x, y):
        plt.text(
            xy[0] - 0.5,
            xy[1],
            int(xy[1]),
            {
                "weight": "bold",
                "size": 10,
            },
        )
    plt.title(
        f"Predicted Ratings for {player.name} over time",
        fontdict={"weight": "bold"},
    )
    plt.xlabel("Age")
    plt.ylabel("Predicted Rating")
    plt.axvline(x[np.argmax(y)], color="lightgray", linestyle="--")
    plt.show()


def plotPlayer(player, axes, config, date=None):
    labelsOn, _, projectionOn, scaleForOverallRatingOn = list(config.values())
    blank = True if player is None else False
    axes.set(aspect="equal")
    frameSize = 2.5
    frameSize = frameSize * 100 if scaleForOverallRatingOn else frameSize

    if not blank:
        ### Calculate vertices
        skillDistribution = player.getSkillDistribution(player.getAgeOnDate(date))
        playerRating = player.ratings[date]["rating"] if date is not None else player.rating
        points = {}
        for j, (skill, value) in enumerate(skillDistribution.items()):
            if scaleForOverallRatingOn:
                value *= playerRating
            angle = 2 / len(skillDistribution) * j * np.pi
            pointX = value * np.sin(angle)
            pointY = value * np.cos(angle)
            points[skill] = {"x": pointX, "y": pointY}
            if labelsOn:
                sidePointX = frameSize * np.sin(angle)
                sidePointY = frameSize * np.cos(angle)
                labelX = 290 * np.sin(angle)
                labelY = 290 * np.cos(angle)
                axes.plot((0, sidePointX), (0, sidePointY), color="blue", linewidth=0.25)
                labelText = (
                    f"{skill.capitalize()}\n{int(value)}"
                    if scaleForOverallRatingOn
                    else f"{skill}\n{value:.1%}"
                )
                axes.text(
                    labelX,
                    labelY,
                    labelText,
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontdict={"family": "arial", "size": 15},
                )
        pointsList = list(points.values())
        pointsList.append(
            pointsList[0]
        )  ### Duplicate first point as last point to complete the shape

        ### Add edges between vertices
        for j in range(len(pointsList) - 1):
            axes.plot(
                (pointsList[j]["x"], pointsList[j + 1]["x"]),
                (pointsList[j]["y"], pointsList[j + 1]["y"]),
                color="black",
            )

        ### Add rating projection to plot
        if projectionOn and player.age != player.peakAge:
            projectedSkillDistribution = player.getSkillDistribution(player.peakAge)
            projectedPlayerRating = player.getRating(age=player.peakAge)
            projectedPoints = {}
            for j, (skill, projectedValue) in enumerate(projectedSkillDistribution.items()):
                if scaleForOverallRatingOn:
                    projectedValue *= projectedPlayerRating
                angle = 2 / len(projectedSkillDistribution) * j * np.pi
                projectedPointX = projectedValue * np.sin(angle)
                projectedPointY = projectedValue * np.cos(angle)
                projectedPoints[skill] = {"x": projectedPointX, "y": projectedPointY}
            projectedPointsList = list(projectedPoints.values())
            projectedPointsList.append(
                projectedPointsList[0]
            )  ### Duplicate first point as last point to complete the shape

            ### Add edges between vertices
            projectedLineColour = "green" if player.age < player.peakAge else "red"

            for j in range(len(projectedPointsList) - 1):
                axes.plot(
                    (projectedPointsList[j]["x"], projectedPointsList[j + 1]["x"]),
                    (projectedPointsList[j]["y"], projectedPointsList[j + 1]["y"]),
                    color=projectedLineColour,
                    linestyle="dotted",
                )

    if not blank:
        xPoints = [point["x"] for point in pointsList]
        yPoints = [point["y"] for point in pointsList]
    else:
        xPoints = [frameSize, frameSize, -frameSize, -frameSize]
        yPoints = [frameSize, -frameSize, -frameSize, frameSize]
    axes.fill(xPoints, yPoints, color="lightgray")

    ### Miscellaneous config
    axes.set_xlim(-frameSize, frameSize)
    axes.set_ylim(-frameSize, frameSize)
    axes.axis("off")
    if not blank and not labelsOn:
        axes.plot(0, 0, "o")


def showSkillDistribution(
    players, date=None, labels=None, projection=False, scaleForOverallRating=True
):
    if not isinstance(players, list):
        players = [players]
    numPlayers = len(players)
    if numPlayers > 10:
        print("Too many players")
        return
    if labels is None:
        if numPlayers > 2:
            labels = False
        else:
            labels = True
    positionTextRotated = True if numPlayers > 2 else False
    plotConfig = {
        "labelsOn": labels,
        "positionTextRotated": positionTextRotated,
        "projectionOn": projection,
        "scaleForOverallRatingOn": scaleForOverallRating,
    }
    rows = 1 if numPlayers < 3 else 2
    cols = math.ceil(numPlayers / rows)
    fig, axes = plt.subplots(nrows=rows, ncols=cols)
    if numPlayers == 1:
        plotPlayer(players[0], axes, plotConfig, date)
    elif numPlayers == 2:
        for i in range(cols):
            plotPlayer(players[i], axes[i], plotConfig, date)
    else:
        p = 0
        for i in range(rows):
            for j in range(cols):
                if p < numPlayers:
                    plotPlayer(players[p], axes[i][j], plotConfig, date)
                else:
                    plotPlayer(None, axes[i][j], plotConfig, date)
                p += 1

    # ### Show plot
    # plt.show()
    plt.tight_layout()
    return fig


def showPlayerForm(player):
    fig = plt.figure()
    fig.add_subplot(111)
    x = list(player.forms.keys())
    y = list(player.forms.values())
    x = mdates.date2num(x)
    plt.axis("off")
    plt.plot_date(x, y, "b-")
    return fig


def showPlayerDevelopment(player, date=None):
    fig = plt.figure()
    fig.add_subplot(111)
    if date is not None:
        x = range(len([k for k in player.ratings.keys() if k <= date]))
        yR = [v["rating"] for k, v in player.ratings.items() if k <= date]
        yPR = [v["peakRating"] for k, v in player.ratings.items() if k <= date]
    else:
        x = range(len(player.ratings.keys()))
        yR = [v["rating"] for v in player.ratings.values()]
        yPR = [v["peakRating"] for v in player.ratings.values()]
    plt.title("Development Graph", fontsize=14)
    plt.xlabel("Day", fontsize=12, labelpad=8)
    plt.ylabel("Rating", fontsize=12, labelpad=8)
    fadeRange = 10
    for plot, colorTuple in zip([yR, yPR], [[0, 0, 1], [0.68, 0.85, 0.90]]):
        for i in range(0, fadeRange + 1):
            for y, strength in zip([plot[0], plot[-1]], [1 - (i / fadeRange), 0 + (i / fadeRange)]):
                plt.gca().axhline(
                    y,
                    (1 / fadeRange) * i - (1 / fadeRange),  ### xmin
                    (1 / fadeRange) * i,  ### xmax
                    color=colorTuple + [strength],
                    linestyle="--",
                    linewidth=max(strength, 0.1),
                )
    plt.plot(x, yR, "b-")
    plt.plot(x, yPR, color="lightblue", linestyle="solid")
    return fig
