import utils
import config
import random
import numpy as np
import copy
from scipy import spatial

class Player:
    def __init__(self, controller, id):
        self.controller = controller
        self.id = id
        self.name = utils.generatePlayerName()
        self.setBirthDate()
        self.setAge()
        self.retired = False
        self.setPeakAge()
        self.setGrowthSpeed()
        self.setRetirementThreshold()
        self.setPeakRating()
        self.setRating()
        self.setUnderlyingSkillDistribution()
        self.setSkillDistribution()
        self.setSkillValues()
        self.setPositionRatings()
        self.injured = False
        self.fatigue = 0
        self.playerReports = []
        self.injuries = []
        self.form = 0
        self.ratings = {}
        self.forms = {}
        
    def setBirthDate(self):
        agMin, agMax = config.playerConfig['age']['min'], config.playerConfig['age']['max']
        age = random.randint(agMin, agMax)
        self.birthDate = utils.getBirthDate(config.timeConfig['startDate'], age)
    
    def getAge(self, dp = None):
        return round(self.age, dp) if dp is not None and dp > 0 else int(self.age)
    
    def setAge(self):
        td = self.controller.universe.currentDate - self.birthDate
        self.age = td.days / 365.25

    def setPeakAge(self):
        self.peakAge = utils.limitedRandNorm(config.playerConfig['peakAge'])
    
    def setGrowthSpeed(self):
        randIncline = utils.limitedRandNorm(config.playerConfig['growthSpeed']['incline'])
        randDecline = utils.limitedRandNorm(config.playerConfig['growthSpeed']['decline'])
        self.growthSpeed = {
            'incline': randIncline,
            'decline': randDecline
        }

    def setRetirementThreshold(self):
        self.retirementThreshold = utils.limitedRandNorm(config.playerConfig['retirementThreshold'])

    def setPeakRating(self):
        self.peakRating = utils.limitedRandNorm(config.playerConfig['peakRating'])

    def adjustPeakRating(self):
        mn, mx = config.playerConfig['peakRating']['min'], config.playerConfig['peakRating']['max']
        self.peakRating = utils.limitedRandNorm({'mu': self.peakRating, 'sigma': 50 / (self.age ** 2), 'mn': mn, 'mx': mx})

    def getRating(self, age = None):
        age = self.age if age is None else age
        distanceFromPeakAge = abs(self.peakAge - age)
        direction = 'incline' if self.peakAge > age else 'decline'
        growthSpeedFactor = self.growthSpeed[direction]
        peakRatingFulfillment = 1 - (distanceFromPeakAge ** 1.5 * 0.01 * growthSpeedFactor)
        rating = self.peakRating * peakRatingFulfillment
        return rating

    def setRating(self):
        self.rating = self.getRating()
        direction = 'incline' if self.peakAge > self.age else 'decline'
        if direction == 'decline' and self.rating < (self.peakRating * self.retirementThreshold) and self.retired is False:
            self.retire()

    def rebalanceSkillDistribution(self, distribution):
        [skDiMn, skDiMx] = [value for value in list(config.playerConfig['skill']['distribution'].values())[2:4]]
        x = len(config.playerConfig['skill']['skills'])
        while True:
            skillsOutOfBounds = []
            for value in distribution.values():
                if value < skDiMn or value > skDiMx:
                    skillsOutOfBounds.append(1)
                else:
                    skillsOutOfBounds.append(0)
            # skillsOutOfBounds = [1 for value in distribution.values() if value < skDiMin or value > skDiMax else 0]
            if not any(skillsOutOfBounds):
                break
            for key, value in distribution.items():
                distribution[key] = ((value * x) + len(distribution) - x) / len(distribution)
            x -= 0.1
    
    def setUnderlyingSkillDistribution(self):
        skills = config.playerConfig['skill']['skills']
        [skDiMu, skDiSg] = [value for value in list(config.playerConfig['skill']['distribution'].values())[0:2]]
        underlyingSkillDistribution = {skill: np.random.normal(skDiMu, skDiSg) for skill in skills}

        ### Centralise - set mean = 1
        totalSkill = sum(underlyingSkillDistribution.values())
        for key, value in underlyingSkillDistribution.items():
            underlyingSkillDistribution[key] = value * len(skills) / totalSkill
        
        ### Rebalance - handle the passing of thresholds for minimum and maximum
        self.rebalanceSkillDistribution(underlyingSkillDistribution)

        self.underlyingSkillDistribution = underlyingSkillDistribution
    
    def getSkillDistribution(self, age = None):
        skillDistribution = copy.deepcopy(self.underlyingSkillDistribution)

        ### Apply age-dependent modifications to distribution
        age = self.age if age is None else age
        transitions = config.playerConfig['skill']['transitions']
        distanceFromPeakAge = self.peakAge - age
        for transition in transitions:
            direction = 'incline' if self.peakAge > age else 'decline'
            if (direction == 'incline' and transition['when']['incline'] == True) or (direction == 'decline' and transition['when']['decline'] == True):
                if transition['from'] == '':
                    toValue = skillDistribution[transition['to']]
                    toFactor = toValue / sum(skillDistribution.values())
                    modifiedToFactor = toFactor - (distanceFromPeakAge * transition['gradient'])
                    skillDistribution[transition['to']] = sum(skillDistribution.values()) * modifiedToFactor
                elif transition['to'] == '':
                    fromValue = skillDistribution[transition['from']]
                    fromFactor = fromValue / sum(skillDistribution.values())
                    modifiedFromFactor = fromFactor - (distanceFromPeakAge * transition['gradient'])
                    skillDistribution[transition['from']] = sum(skillDistribution.values()) * modifiedFromFactor
                else:
                    fromValue = skillDistribution[transition['from']]
                    toValue = skillDistribution[transition['to']]
                    fromToSum = fromValue + toValue
                    fromFactor = fromValue / fromToSum
                    modifiedFromFactor = fromFactor - (distanceFromPeakAge * transition['gradient'])
                    skillDistribution[transition['from']] = fromToSum * modifiedFromFactor
                    skillDistribution[transition['to']] = fromToSum * (1 - modifiedFromFactor)
                self.rebalanceSkillDistribution(skillDistribution)
        
        ### Identify player's best position and normalise player's skill distribution towards the optimum for that position, to curb excessive weirdness
        bestPosition = self.getBestPosition(skillDistribution)
        bestSkillDistribution = config.playerConfig['positions'][bestPosition]['skillDistribution']
        normalisingFactor = config.playerConfig['skill']['normalisingFactor']
        for skill, value in skillDistribution.items():
            skillDistribution[skill] = skillDistribution[skill] + (bestSkillDistribution[skill] - skillDistribution[skill]) * utils.limitedRandNorm(normalisingFactor)

        ### Centralise - restore mean to 1
        totalSkill = sum(skillDistribution.values())
        for key, value in skillDistribution.items():
            skillDistribution[key] = value * len(skillDistribution.values()) / totalSkill

        return skillDistribution

    def setSkillDistribution(self):
        self.skillDistribution = self.getSkillDistribution()

    def getSkillValues(self, rating = None, skillDistribution = None):
        rating = self.rating if rating is None else rating
        skillDistribution = self.skillDistribution if skillDistribution is None else skillDistribution
        skillValues = {skill: rating * value for skill, value in skillDistribution.items()}
        return skillValues
    
    def setSkillValues(self):
        self.skillValues = self.getSkillValues()

    def getPositionSuitabilities(self, skillDistribution = None):
        positions = config.playerConfig['positions']
        skillDistribution = self.skillDistribution if skillDistribution is None else skillDistribution
        positionSuitabilities = {}
        selfSkillDistribution = list(skillDistribution.values())
        for position, attributes in positions.items():
            idealSkillDistributionForPosition = list(attributes['skillDistribution'].values())
            positionSuitability = 1 - spatial.distance.cosine(selfSkillDistribution, idealSkillDistributionForPosition)
            positionSuitability = 1 - np.power(1 - positionSuitability, (2 / 3))
            positionSuitabilities[position] = positionSuitability
        maxPositionSuitability = max(positionSuitabilities.values())
        for position in positionSuitabilities.keys():
            positionSuitabilities[position] *= 1 / maxPositionSuitability
        return positionSuitabilities

    def getBestPosition(self, skillDistribution = None):
        positionSuitabilities = self.getPositionSuitabilities() if skillDistribution is None else self.getPositionSuitabilities(skillDistribution)
        bestPosition = max(positionSuitabilities, key = positionSuitabilities.get)
        return bestPosition
    
    def setBestPosition(self):
        self.bestPosition = self.getBestPosition()
    
    def getPositionRatings(self, rating = None, skillDistribution = None):
        rating = self.rating if rating is None else rating
        skillDistribution = self.skillDistribution if skillDistribution is None else skillDistribution
        positionSuitabilities = self.getPositionSuitabilities(skillDistribution)
        positionRatings = {position: rating * value for position, value in positionSuitabilities.items()}
        return positionRatings

    def setPositionRatings(self):
        self.positionRatings = self.getPositionRatings()

    def retire(self):
        self.retired = True
        if hasattr(self, 'club') and self.club and self in self.club.players:
            self.club.players.remove(self)
            self.club = None
    
    def recover(self):
        fatigueReduction = np.sqrt(self.skillValues['fitness']) / 100
        self.fatigue -= fatigueReduction
        self.fatigue = 0 if self.fatigue < 0 else self.fatigue
        if self.injured:
            self.injured -= 1
        if self.injured == 0:
            self.injured = False
        self.form -= self.form / 25
    
    def injure(self):
        if self.club is not None and self.injured is False:
            injury = True if np.random.normal(self.fatigue, 0.02) > 0.25 else False
            if injury:
                x, itemArray, probabilityArray = 1, [], []
                for i in range(1, 366):
                    x /= 1.05
                    itemArray.append(i)
                    probabilityArray.append(x)
                probabilityArray = [probability / sum(probabilityArray) for probability in probabilityArray]
                injuryLength = np.random.choice(itemArray, p = probabilityArray)
                self.injured = injuryLength
                self.injuries.append([self.club.league.system.universe.currentDate, injuryLength])

    def advance(self):
        self.injure()
        self.setAge()
        self.recover()
        self.adjustPeakRating()
        self.setRating()
        self.setSkillDistribution()
        self.setSkillValues()
    
    def handlePlayerReport(self, playerReport):
        if playerReport not in self.playerReports: ### Prevent duplication from Universal Tournament group stage matches, which are handled by both the group and the wider tournament
            self.playerReports.append(playerReport)
            self.fatigue += playerReport['fatigueIncrease']
            self.form += playerReport['gravitatedMatchForm']
    
    def getProperName(self, forenameStyle = 'Whole', surnameStyle = 'Whole'):
        ### Both forenameStyle and surnameStyle arguments can be set to either 'Empty', 'Shortened' or 'Whole'
        forename, surname = self.name[0], self.name[1]
        properNameArray = []
        for style, name in zip([forenameStyle, surnameStyle], [forename, surname]):
            if style == 'Shortened':
                properNameArray.append(name[0] + '.')
            elif style == 'Whole':
                properNameArray.append(name)
        return ' '.join(properNameArray)
    
    def retire(self):
        self.retired = True
        self.controller.retirePlayer(self)
        if hasattr(self, 'club') and self.club:
            self.club.players.remove(self)
            self.club = None