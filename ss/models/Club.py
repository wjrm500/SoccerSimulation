from .. import config
import numpy as np
import copy
from .Select import Select
from .Team import Team
import re

class Club:
    def __init__(self, league, city):
        self.id = city['_id']
        self.name = city['city_name']
        self.league = league
        self.players = []
        numPlayersPerClub = league.system.universe.config['numPlayersPerClub'] or config.systemConfig['numPlayersPerClub']
        for _ in range(numPlayersPerClub):
            player = self.league.system.universe.playerController.createPlayer()
            self.players.append(player)
            player.club = self
            self.alterPlayerRatingEasterEgg(player)
        self.favouriteFormation = self.setFavouriteFormation()
    
    def alterPlayerRatingEasterEgg(self, player):
        if self.name in ['Arsenal', 'Arsenal FC', 'Gunners', 'The Gunners', 'Newcastle', 'Newcastle United', 'Newcastle United FC', 'The Toon', 'Toon Army']:
            player.peakRating -= 10
            player.setRating()
            player.setSkillValues()
            player.setPositionRatings()
        elif self.name in ['Liverpool', 'Liverpool FC']:
            player.peakRating += 10
            player.setRating()
            player.setSkillValues()
            player.setPositionRatings()
    
    def getProvisionalShortName(self, precedence = 0):
        ### If precedence = 0, use all available consonants
        ### If precedence = 1, ignore third consonant
        ### If precedence = 2, ignore third and fourth consonants
        ### Etc.
        firstLetterAndConsonantsOnly = self.name[0] + re.sub('(?i)[aeiou -\.,]', '', self.name[1:])
        provisionalShortName = (firstLetterAndConsonantsOnly[:precedence + 3] if len(firstLetterAndConsonantsOnly) >= precedence + 3 else self.name[:3]).upper()
        provisionalShortName = provisionalShortName[:2] + provisionalShortName[-1:]
        return provisionalShortName

    def getShortName(self):
        ### Need to ensure no short name clashes with clubs in same league
        ### Basic idea is that clubs with higher ratings receive higher precedence when it comes to "naming rights"
        ### So we find all clubs in league whose provisional short names clash initially
        ### Then we see where this particular club ranks amongst this set of clashing clubs
        ### We then feed this rank as the argument to precedence in the getProvisionalShortName method
        shortName = self.getProvisionalShortName()
        clashingClubs = []
        for club in self.league.clubs:
            if shortName == club.getProvisionalShortName():
                clashingClubs.append(club)
        selfRankAmongClashingClubs = sorted(clashingClubs, key = lambda x: x.getRating(), reverse = True).index(self)
        return self.getProvisionalShortName(precedence = selfRankAmongClashingClubs)
    
    def setFavouriteFormation(self):
        formations, weights = [], []
        for key, value in config.formationConfig.items():
            formations.append(key)
            weights.append(value['popularity'])
        return np.random.choice(formations, size = 1, p = weights)[0]
            
    def selectTeam(self, homeAway = 'neutral', squad = None, test = False):
        try:
            squad = self.players if squad is None else squad
            if len(squad) < 10:
                raise Exception('Not enough players to form a full team.')
            chosenFormation = self.favouriteFormation
            personnelRequired = copy.deepcopy(config.formationConfig[chosenFormation]['personnel'])
            selection = []
            while sum(personnelRequired.values()) > 0:
                maxValue = 0
                for position, numPlayers in personnelRequired.items():
                    if numPlayers > 0:
                        for player in squad:
                            if player not in [select.player for select in selection] and (False if test else player.injured) is False:
                                selectRating = player.positionRatings[position]
                                selectRating -= 0 if test else selectRating * player.fatigue
                                selectRating += 0 if test else (selectRating * player.form) / 10
                                selectRating *= config.matchConfig['homeAwayDifferential'][homeAway]
                                if selectRating > maxValue:
                                    maxValue = selectRating
                                    select = Select(player, position, selectRating)
                personnelRequired[select.position] -= 1
                selection.append(select)
            return Team(self, chosenFormation, selection)
        except:
            return None
    
    def getRating(self, decimalPlaces = 2):
        return round(np.mean([player.rating for player in self.players]), decimalPlaces)
    
    def getMatchReports(self, gameweek = None):
        matchReports = [matchReport for matchReport in self.league.matchReports if self in matchReport['clubs']]
        if gameweek is None:
            return matchReports
        return [matchReport for matchReport in matchReports if matchReport['gameweek'] <= gameweek]