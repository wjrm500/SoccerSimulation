import sys
sys.path.append('.')
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import dates as mdates
from models.Player import Player
from config import playerConfig
from types import SimpleNamespace
import math
import copy

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
                'weight': 'bold',
                'size'  : 10,
            }
        )
    plt.title(
        'Predicted Ratings for {} over time'.format(player.name),
        fontdict = {
            'weight': 'bold'
        }
    )
    plt.xlabel('Age')
    plt.ylabel('Predicted Rating')
    plt.axvline(
        x[np.argmax(y)],
        color = 'lightgray',
        linestyle = '--'
    )
    plt.show()

def plotPlayer(player, axes, config):
    labelsOn, positionTextRotated, projectionOn, scaleForOverallRatingOn = [value for value in list(config.values())]
    blank = True if player is None else False
    axes.set(aspect='equal')
    frameSize = 2.5
    frameSize = frameSize * 100 if scaleForOverallRatingOn else frameSize

    if not blank:
        ### Calculate vertices
        skillDistribution = player.skillDistribution
        playerRating = player.rating
        points = {}
        for j, (skill, value) in enumerate(skillDistribution.items()):
            if scaleForOverallRatingOn:
                value *= playerRating
            angle = 2 / len(skillDistribution) * j * np.pi
            pointX = value * np.sin(angle)
            pointY = value * np.cos(angle)
            points[skill] = {'x': pointX, 'y': pointY}
            if labelsOn:
                sidePointX = frameSize * np.sin(angle)
                sidePointY = frameSize * np.cos(angle)
                # labelOffset = 37.5 if scaleForOverallRatingOn else 0.375
                # labelX = (value + labelOffset) * np.sin(angle)
                # labelY = (value + labelOffset) * np.cos(angle)
                labelX = 290 * np.sin(angle)
                labelY = 290 * np.cos(angle)
                axes.plot((0, sidePointX), (0, sidePointY), color = 'blue', linewidth = 0.25)
                labelText = "{}\n{}".format(skill.capitalize(), int(value)) if scaleForOverallRatingOn else "{0}\n{1:.1%}".format(skill, value)
                axes.text(labelX, labelY, labelText, horizontalalignment = 'center', verticalalignment = 'center', fontdict = {'family': 'arial', 'size': 15})
        pointsList = list(points.values())
        pointsList.append(pointsList[0]) ### Duplicate first point as last point to complete the shape

        ### Add edges between vertices
        for j in range(len(pointsList) - 1):
            axes.plot(
                (pointsList[j]['x'], pointsList[j + 1]['x']),
                (pointsList[j]['y'], pointsList[j + 1]['y']),
                color = 'black'
            )

        ### Add rating projection to plot
        if projectionOn and player.age != player.peakAge:
            projectedSkillDistribution = player.getSkillDistribution(player.peakAge)
            projectedPlayerRating = player.getRating(age = player.peakAge)
            projectedPoints = {}
            for j, (skill, projectedValue) in enumerate(projectedSkillDistribution.items()):
                if scaleForOverallRatingOn:
                    projectedValue *= projectedPlayerRating
                angle = 2 / len(projectedSkillDistribution) * j * np.pi
                projectedPointX = projectedValue * np.sin(angle)
                projectedPointY = projectedValue * np.cos(angle)
                projectedPoints[skill] = {'x': projectedPointX, 'y': projectedPointY}
            projectedPointsList = list(projectedPoints.values())
            projectedPointsList.append(projectedPointsList[0]) ### Duplicate first point as last point to complete the shape

            ### Add edges between vertices
            projectedLineColour = 'green' if player.age < player.peakAge else 'red'

            for j in range(len(projectedPointsList) - 1):
                axes.plot(
                    (projectedPointsList[j]['x'], projectedPointsList[j + 1]['x']),
                    (projectedPointsList[j]['y'], projectedPointsList[j + 1]['y']),
                    color = projectedLineColour,
                    linestyle = 'dotted'
                )

    if not blank:
        xPoints = [point['x'] for point in pointsList]
        yPoints = [point['y'] for point in pointsList]
    else:
        xPoints = [frameSize, frameSize, -frameSize, -frameSize]
        yPoints = [frameSize, -frameSize, -frameSize, frameSize]
    axes.fill(xPoints, yPoints, color = 'lightgray')

    ### Frame plot/s with grey border
    # axes.plot((-frameSize, frameSize), (frameSize, frameSize), color = "lightgray")
    # axes.plot((frameSize, frameSize), (-frameSize, frameSize), color = "lightgray")
    # axes.plot((-frameSize, frameSize), (-frameSize, -frameSize), color = "lightgray")
    # axes.plot((-frameSize, -frameSize), (-frameSize, frameSize), color = "lightgray")

    ### Miscellaneous config
    axes.set_xlim(-frameSize, frameSize)
    axes.set_ylim(-frameSize, frameSize)
    axes.axis('off')
    if not blank and not labelsOn:
        axes.plot(0, 0, 'o')

    ### Add corner text
    # if not blank:
    #     cornerFontDict = {
    #         'family': 'arial',
    #         'size': 9,
    #         'weight': 'bold'
    #     }
    #     axes.text(
    #         -0.975 * frameSize,
    #         0.95 * frameSize,
    #         '{}\n{}'.format(player.name[0], player.name[1]),
    #         horizontalalignment = 'left',
    #         verticalalignment = 'top',
    #         fontdict = (lambda a, b: a.update(b) or a)(copy.deepcopy(cornerFontDict), {'size': 10})
    #     )
    #     axes.text(
    #         0.975 * frameSize,
    #         0.95 * frameSize,
    #         'Age: {}\nRating: {}'.format(int(player.age), int(player.rating)),
    #         horizontalalignment = 'right',
    #         verticalalignment = 'top',
    #         fontdict = cornerFontDict
    #     )
    #     axes.text(
    #         0.975 * frameSize,
    #         -0.95 * frameSize,
    #         'Peak Age: {}\nPeak Rating: {}'.format(int(player.peakAge), int(player.peakRating)),
    #         horizontalalignment = 'right',
    #         verticalalignment = 'bottom',
    #         fontdict = cornerFontDict
    #     )
    #     poSuDict = player.getPositionSuitabilities()
    #     bestPosition = player.getBestPosition()
    #     if not positionTextRotated:
    #         positionText = ''
    #         for position in sorted(poSuDict, key = poSuDict.get, reverse = True):
    #             suitability = poSuDict[position]
    #             if suitability >= 0.975:
    #                 positionText += '{0}: {1:.1%}\n'.format(
    #                     playerConfig['positions'][position]['realName'],
    #                     suitability
    #                 )
    #         if positionText == '':
    #             positionText = '{0}: {1:.1%}'.format(
    #                 playerConfig['positions'][bestPosition]['realName'],
    #                 poSuDict[bestPosition]
    #             )
    #         else:
    #             positionText = positionText.rstrip()
    #         axes.text(
    #             -0.975 * frameSize,
    #             -0.95 * frameSize,
    #             positionText,
    #             horizontalalignment = 'left',
    #             verticalalignment = 'bottom',
    #             fontdict = cornerFontDict
    #         )
    #     else:
    #         realPositionName = playerConfig['positions'][bestPosition]['realName']
    #         positionText = realPositionName.replace(' ', '\n')
    #         axes.text(
    #             -0.975 * frameSize,
    #             -0.95 * frameSize,
    #             positionText,
    #             horizontalalignment = 'left',
    #             verticalalignment = 'bottom',
    #             fontdict = cornerFontDict,
    #             rotation = 90
    #         )

def showSkillDistribution(players, labels = None, projection = False, scaleForOverallRating = True):
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
        'labelsOn': labels,
        'positionTextRotated': positionTextRotated,
        'projectionOn': projection,
        'scaleForOverallRatingOn': scaleForOverallRating
    }
    rows = 1 if numPlayers < 3 else 2
    cols = math.ceil(numPlayers / rows)
    fig, axes = plt.subplots(nrows = rows, ncols = cols)
    if numPlayers == 1:
        plotPlayer(players[0], axes, plotConfig)
    elif numPlayers == 2:
        for i in range(cols):
            plotPlayer(players[i], axes[i], plotConfig)
    else:
        p = 0
        for i in range(rows):
            for j in range(cols):
                if p < numPlayers:
                    plotPlayer(players[p], axes[i][j], plotConfig)
                else:
                    plotPlayer(None, axes[i][j], plotConfig)
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
    plt.axis('off')
    plt.plot_date(x, y, 'b-')
    return fig