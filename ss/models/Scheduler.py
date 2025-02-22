import copy
from datetime import date, timedelta

from .Fixture import Fixture


class Scheduler:
    fixtures_created = 0

    @classmethod
    def schedule_fixture(cls, date, gameweek, tournament, club_x, club_y):
        if not hasattr(tournament, "fixtures"):
            tournament.fixtures = []
        cls.fixtures_created += 1
        fixture = Fixture(copy.copy(cls.fixtures_created), tournament, date, club_x, club_y)
        fixture.set_gameweek(gameweek)
        tournament.fixtures.append(fixture)

    @classmethod
    def schedule_league_fixtures(cls, year, league, weekday=5):
        schedule = cls.round_robin_scheduler(league, robin_type="double")
        current_date = date(year, 1, 1)
        gameweek = 1
        while True:
            if current_date.year > year or not schedule.get(
                gameweek
            ):  ### Exit loop when year changes / when fixtures have been exhausted
                return
            if current_date.weekday() == weekday:
                for game in schedule[gameweek]:
                    club_x, club_y = game["home"], game["away"]
                    cls.schedule_fixture(current_date, gameweek, league, club_x, club_y)
                gameweek += 1
            current_date += timedelta(days=1)

    @classmethod
    def spread_schedule_league_fixtures(cls, year, league):
        schedule = cls.round_robin_scheduler(league, robin_type="double")
        gameweek = 1
        game_day_of_year = 1
        game_interval = 300 / len(schedule)
        league.gameweek_dates = {}
        while True:
            if not schedule.get(gameweek):  ### Exit loop when fixtures have been exhausted
                return
            game_date = date(year, 1, 1) + timedelta(round(game_day_of_year) - 1)
            for game in schedule[gameweek]:
                club_x, club_y = game["home"], game["away"]
                cls.schedule_fixture(game_date, gameweek, league, club_x, club_y)
            league.gameweek_dates[gameweek] = game_date
            gameweek += 1
            game_day_of_year += game_interval

    @classmethod
    def round_robin_scheduler(cls, tournament, robin_type="single", returned_object="dict"):
        num_clubs = len(tournament.clubs)
        if num_clubs % 2 != 0:
            raise Exception("Number of clubs must be even")
        schedule = []
        fixtures_per_week = int(num_clubs / 2)
        max_index = fixtures_per_week - 1
        for i in range(num_clubs - 1):
            new_gameweek = {}
            if i == 0:
                clubs_for_popping = copy.copy(tournament.clubs)
                for j in range(fixtures_per_week):
                    new_gameweek[j] = [clubs_for_popping.pop(0), clubs_for_popping.pop()]
            else:
                last_gameweek = schedule[i - 1]
                for j in range(fixtures_per_week):
                    if j == 0:
                        club_one = tournament.clubs[0]
                    elif j == 1:
                        club_one = last_gameweek[0][1]
                    else:
                        club_one = last_gameweek[j - 1][0]

                    if j != max_index:
                        club_two = last_gameweek[j + 1][1]
                    else:
                        club_two = last_gameweek[max_index][0]

                    new_gameweek[j] = [club_one, club_two]
            schedule.append(new_gameweek)

        for i, gameweek in enumerate(schedule):
            if i % 2 != 0:  ### If index is odd - to only flip teams on alternate gameweeks
                for key, value in gameweek.items():
                    gameweek[key] = [value[1], value[0]]  ### Flip home and away teams

        if robin_type == "double":  ### If double round-robin
            flipped_schedule = [
                copy.copy(gameweek) for gameweek in schedule
            ]  ### copy.copy(schedule) does not work because the list objects containing clubs in
            ### schedule are mutated // copy.deepcopy(schedule) does not work because club objects
            ### are duplicated so effectively a separate set of clubs is referenced in second half
            ### of schedule
            for gameweek in flipped_schedule:
                for key, value in gameweek.items():
                    gameweek[key] = [value[1], value[0]]  ### Flip home and away teams
            schedule = schedule + flipped_schedule

        reformatted_schedule = {}
        for i, gameweek in enumerate(schedule):
            if returned_object == "dict":
                fixture_list = [{"home": value[0], "away": value[1]} for value in gameweek.values()]
            elif returned_object == "fixture":
                fixture_list = [
                    Fixture(tournament, club_x=value[0], club_y=value[1])
                    for value in gameweek.values()
                ]
            reformatted_schedule[i + 1] = fixture_list
        return reformatted_schedule
