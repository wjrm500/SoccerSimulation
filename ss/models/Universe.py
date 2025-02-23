import datetime

from .. import config
from .PlayerController import PlayerController
from .Scheduler import Scheduler
from .System import System


class _Universe:
    def __init__(self, custom_config=None, system_ids=None):
        self.current_date = config.time_config["start_date"]
        self.player_controller = PlayerController(self)
        self.config = custom_config
        self.systems = []
        if system_ids is not None:
            for system_id in system_ids:
                self.systems.append(System(self, system_id))
        else:
            num_systems = custom_config["num_systems"] or config.system_config["num_systems"]
            for _ in range(num_systems):
                self.systems.append(System(self))
        self.schedule_leagues()

    def time_travel(self, days, r):
        for i in range(days):
            simulation_progress = i / (days - 1)
            print(f"i = {i}; Days = {days}; Simulation Progress = {simulation_progress}")
            r.set("simulation_progress_" + self.universe_key, simulation_progress)
            self.resolve_quotidia()
            self.advance_one_day()

    def resolve_quotidia(self):
        self.play_fixtures(self.current_date)

    def play_fixtures(self, date):
        for system in self.systems:
            for league in system.leagues:
                league.play_outstanding_fixtures(date)

    def advance_one_day(self):
        self.current_date += datetime.timedelta(days=1)
        self.player_controller.advance()

    def schedule_leagues(self):
        for system in self.systems:
            for league in system.leagues:
                Scheduler.schedule_league_fixtures(self.current_date.year, league)

    def get_club_by_id(self, club_id):
        for system in self.systems:
            for league in system.leagues:
                for club in league.clubs:
                    if club.id == int(club_id):
                        return club

    def get_club_by_name(self, club_name):
        for system in self.systems:
            for league in system.leagues:
                for club in league.clubs:
                    if club.name == club_name:
                        return club

    def get_fixture_by_id(self, fixture_id):
        for system in self.systems:
            for league in system.leagues:
                for fixture in league.fixtures:
                    if fixture.id == int(fixture_id):
                        return fixture


_instance = None


def Universe(custom_config=None, system_ids=None):
    global _instance
    if _instance is None:
        _instance = _Universe(custom_config, system_ids)
    return _instance
