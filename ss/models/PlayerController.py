import copy

from .Player import Player


class PlayerController:
    def __init__(self, universe):
        self.universe = universe
        self.players, self.players_created = [], 0
        self.active_players, self.retired_players, self.free_agent_players = [], [], []

    def get_player_by_id(self, id):
        id = int(id)
        for player in self.players:
            if player.id == id:
                return player
        return None

    def get_players_by_name(self, name):
        players = []
        for player in self.players:
            if player.name == name:
                players.append(player)
        return players

    def advance(self):
        for player in self.players:
            player.advance()

    def create_player(self):
        self.players_created += 1
        player = Player(self, id=copy.copy(self.players_created))
        self.players.append(player)
        if hasattr(player, "retired") and player.retired is False:
            self.active_players.append(player)
            self.free_agent_players.append(player)
        return player

    def retire_player(self, player):
        if player not in self.active_players:
            return "Player not active"
        self.active_players.remove(player)
        self.retired_players.append(player)
