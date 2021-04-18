import config
from Player import Player
import numpy as np
import copy
from Select import Select
from Team import Team

class Club:
    def __init__(self, league, city):
        self.id = city['_id']
        self.name = city['city_name']
        self.league = league
        self.players = []
        for _ in range(config.systemConfig['numPlayersPerClub']):
            self.players.append(Player(self))
        self.favouriteFormation = self.setFavouriteFormation()
    
    def setFavouriteFormation(self):
        formations, weights = [], []
        for key, value in config.formationConfig.items():
            formations.append(key)
            weights.append(value['popularity'])
        return np.random.choice(formations, size = 1, p = weights)[0]
            
    def selectTeam(self, homeAway = 'neutral', squad = None):
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
                            if player not in [select.player for select in selection] and player.injured is False:
                                selectRating = player.positionRatings[position]
                                selectRating -= selectRating * player.fatigue
                                selectRating += (selectRating * player.form) / 10
                                if selectRating > maxValue:
                                    maxValue = selectRating
                                    select = Select(player, position, selectRating)
                personnelRequired[select.position] -= 1
                selection.append(select)
            return Team(self, chosenFormation, selection, homeAway)
        except:
            return None