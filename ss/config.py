import datetime

system_config = {
    "num_systems": 1,
    "num_leagues_per_system": 1,
    "num_clubs_per_league": 10,
    "num_players_per_club": 25,
}

time_config = {"start_date": datetime.date(2000, 1, 1)}

formation_config = {
    "3-4-1-2": {
        "popularity": 0.0105,
        "personnel": {"CB": 3, "WB": 2, "CDM": 2, "COM": 1, "CF": 2},
    },
    "3-4-2-1": {
        "popularity": 0.0596,
        "personnel": {"CB": 3, "WB": 2, "CDM": 2, "COM": 2, "CF": 1},
    },
    "3-4-3": {
        "popularity": 0.0589,
        "personnel": {"CB": 3, "WM": 2, "CM": 2, "WF": 2, "CF": 1},
    },
    "3-5-1-1": {
        "popularity": 0.0081,
        "personnel": {"CB": 3, "WB": 2, "CDM": 3, "COM": 1, "CF": 1},
    },
    "3-5-2": {"popularity": 0.0520, "personnel": {"CB": 3, "WM": 2, "CM": 3, "CF": 2}},
    "4-1-3-2": {
        "popularity": 0.0014,
        "personnel": {"FB": 2, "CB": 2, "CDM": 1, "WM": 2, "COM": 1, "CF": 2},
    },
    "4-1-4-1": {
        "popularity": 0.0826,
        "personnel": {"FB": 2, "CB": 2, "CDM": 1, "WM": 2, "COM": 2, "CF": 1},
    },
    "4-2-2-2": {
        "popularity": 0.0056,
        "personnel": {"FB": 2, "CB": 2, "CDM": 2, "COM": 2, "CF": 2},
    },
    "4-2-3-1": {
        "popularity": 0.2121,
        "personnel": {"FB": 2, "CB": 2, "CDM": 2, "WM": 2, "COM": 1, "CF": 1},
    },
    "4-3-1-2": {
        "popularity": 0.0323,
        "personnel": {"FB": 2, "CB": 2, "CDM": 3, "COM": 1, "CF": 2},
    },
    "4-3-2-1": {
        "popularity": 0.0019,
        "personnel": {"FB": 2, "CB": 2, "CDM": 3, "COM": 2, "CF": 1},
    },
    "4-3-3": {
        "popularity": 0.1320,
        "personnel": {"FB": 2, "CB": 2, "CM": 3, "WF": 2, "CF": 1},
    },
    "4-4-1-1": {
        "popularity": 0.0602,
        "personnel": {"FB": 2, "CB": 2, "WB": 2, "CDM": 2, "COM": 1, "CF": 1},
    },
    "4-4-2": {
        "popularity": 0.2216,
        "personnel": {"FB": 2, "CB": 2, "WM": 2, "CM": 2, "CF": 2},
    },
    "4-5-1": {
        "popularity": 0.0101,
        "personnel": {"FB": 2, "CB": 2, "WM": 2, "CM": 3, "CF": 1},
    },
    "5-3-2": {"popularity": 0.0273, "personnel": {"FB": 2, "CB": 3, "CM": 3, "CF": 2}},
    "5-4-1": {
        "popularity": 0.0238,
        "personnel": {"FB": 2, "CB": 3, "WM": 2, "CM": 2, "CF": 1},
    },
}

player_config = {
    "age": {"min": 15, "max": 40},
    "growth_speed": {
        "incline": {"mean": 0.75, "stDev": 0.1, "min": 0.25, "max": 1.25},
        "decline": {"mean": 0.875, "stDev": 0.1, "min": 0.375, "max": 1.375},
    },
    "peak_age": {"mean": 27, "stDev": 2, "min": 22, "max": 32},
    "peak_rating": {"mean": (100 / 3 * 2), "stDev": 10, "min": 20, "max": 100},
    "positions": {
        "CF": {
            "real_name": "Centre Forward",
            "skill_distribution": {
                "offence": 1.52,
                "spark": 1.06,
                "technique": 1.03,
                "defence": 0.69,
                "authority": 0.95,
                "fitness": 0.75,
            },
        },
        "WF": {
            "real_name": "Wing Forward",
            "skill_distribution": {
                "offence": 1.19,
                "spark": 1.35,
                "technique": 1.08,
                "defence": 0.75,
                "authority": 0.69,
                "fitness": 0.94,
            },
        },
        "COM": {
            "real_name": "Centre Offensive Midfielder",
            "skill_distribution": {
                "offence": 1.05,
                "spark": 1.42,
                "technique": 1.48,
                "defence": 0.66,
                "authority": 0.73,
                "fitness": 0.66,
            },
        },
        "WM": {
            "real_name": "Wing Midfielder",
            "skill_distribution": {
                "offence": 1.06,
                "spark": 1.24,
                "technique": 1.06,
                "defence": 0.81,
                "authority": 0.76,
                "fitness": 1.07,
            },
        },
        "CM": {
            "real_name": "Centre Midfielder",
            "skill_distribution": {
                "offence": 0.87,
                "spark": 0.92,
                "technique": 1.04,
                "defence": 0.86,
                "authority": 1.28,
                "fitness": 1.03,
            },
        },
        "CDM": {
            "real_name": "Centre Defensive Midfielder",
            "skill_distribution": {
                "offence": 0.73,
                "spark": 0.84,
                "technique": 0.95,
                "defence": 1.10,
                "authority": 1.23,
                "fitness": 1.15,
            },
        },
        "WB": {
            "real_name": "Wing Back",
            "skill_distribution": {
                "offence": 0.75,
                "spark": 1.03,
                "technique": 1.03,
                "defence": 1.05,
                "authority": 0.68,
                "fitness": 1.46,
            },
        },
        "FB": {
            "real_name": "Full Back",
            "skill_distribution": {
                "offence": 0.73,
                "spark": 0.92,
                "technique": 0.94,
                "defence": 1.24,
                "authority": 0.93,
                "fitness": 1.24,
            },
        },
        "CB": {
            "real_name": "Centre Back",
            "skill_distribution": {
                "offence": 0.72,
                "spark": 0.77,
                "technique": 0.92,
                "defence": 1.35,
                "authority": 1.26,
                "fitness": 0.98,
            },
        },
    },
    "retirement_threshold": {"mean": 0.80, "stDev": 0.025, "min": 0.70, "max": 0.90},
    "skill": {
        "distribution": {"mean": 1, "stDev": 0.375, "min": 0.25, "max": 1.75},
        "normalising_factor": {"mean": 0.5, "stDev": 0.05, "min": 0, "max": 0.5},
        "skills": [
            "offence",
            "spark",  ### A player's ability to create something from nothing
            "technique",
            "defence",
            "authority",  ### How well a player is able to take control of a situation
            "fitness",
        ],
        "transitions": [
            {
                "from": "spark",
                "to": "authority",
                "when": {"incline": True, "decline": True},
                "gradient": -0.01,
            },
            {
                "from": "fitness",
                "to": "",
                "when": {"incline": False, "decline": True},
                "gradient": -0.015,
            },
        ],
    },
}

match_config = {
    "home_away_differential": {"neutral": 1.00, "home": 1.025, "away": 0.975},
    "contribution": {
        "offence": {"offence": 1.0, "defence": 0.0},
        "spark": {"offence": 0.9, "defence": 0.1},
        "technique": {"offence": 0.6, "defence": 0.4},
        "defence": {"offence": 0.0, "defence": 1.0},
        "authority": {"offence": 0.2, "defence": 0.8},
        "fitness": {"offence": 0.3, "defence": 0.7},
    },
    "goal_likelihood": {
        "CF": 1,
        "WF": 0.975,
        "COM": 0.95,
        "WM": 0.95,
        "CM": 0.925,
        "CDM": 0.875,
        "WB": 0.875,
        "FB": 0.85,
        "CB": 0.85,
    },
    "assistLikelihood": {
        "CF": 0.95,
        "WF": 0.975,
        "COM": 1,
        "WM": 1,
        "CM": 0.95,
        "CDM": 0.9,
        "WB": 0.95,
        "FB": 0.925,
        "CB": 0.08,
    },
}
