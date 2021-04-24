import copy
import random
from Player import Player

class PlayerController:
    def __init__(self, universe):
        self.universe = universe
        self.players, self.playersCreated = [], 0
        self.activePlayers, self.retiredPlayers, self.freeAgentPlayers = [], [], []

    def getPlayerById(self, id):
        for player in self.players:
            if player.id == id:
                return player
        return None
    
    def getPlayersByName(self, name):
        players = []
        for player in self.players:
            if player.name == name:
                players.append(player)
        return players
    
    def advance(self):
        for player in self.players:
            player.advance()
    
    def createPlayer(self):
        player = Player(self, id = copy.copy(self.playersCreated))
        self.players.append(player)
        self.playersCreated += 1
        if hasattr(player, 'retired') and player.retired is False:
            self.activePlayers.append(player)
            self.freeAgentPlayers.append(player)
        return player
    
    def retirePlayer(self, player):
        if not player in self.activePlayers:
            return 'Player not active'
        self.activePlayers.remove(player)
        self.retiredPlayers.append(player)