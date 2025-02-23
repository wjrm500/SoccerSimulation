import collections.abc
import os
import random
import re
import string
from datetime import date
from string import ascii_lowercase

import joblib
import numpy as np
from dateutil.relativedelta import relativedelta

from .models.Database import Database


def load_player_names():
    db = Database.get_instance()
    results = db.cnx["soccersim"]["forenames"].find()
    results = list(results)
    global forenames, forename_weights
    forenames = [record["forename"] for record in results]
    forename_counts = [record["count"] for record in results]
    count_sum = sum(forename_counts)
    forename_weights = [record["count"] / count_sum for record in results]

    results = db.cnx["soccersim"]["surnames"].find()
    results = list(results)
    global surnames, surname_weights
    surnames = [record["surname"] for record in results]
    surname_counts = [record["count"] for record in results]
    count_sum = sum(surname_counts)
    surname_weights = [record["count"] / count_sum for record in results]


def sort_mc_and_o_apostrophe(name):
    rx = re.compile(r"(?:(?<=Mc)|(?<=O\'))([a-z])")

    def repl(m):
        char = m.group(1)
        return char.upper()

    return rx.sub(repl, name)


def generate_player_name():
    if "forenames" not in globals():
        load_player_names()
    forename = np.random.choice(forenames, p=forename_weights)
    surname = np.random.choice(surnames, p=surname_weights)
    surname = sort_mc_and_o_apostrophe(surname)
    return (forename, surname)


def generate_random_digits(n):
    return "".join(random.choice(string.digits) for _ in range(n))


def limit_value(value, mn=None, mx=None):
    if mn is not None:
        if value < mn:
            return mn
    if mx is not None:
        if value > mx:
            return mx
    return value


def limited_rand_norm(dictionary):
    [mu, sigma, mn, mx] = list(dictionary.values())
    return limit_value(np.random.normal(mu, sigma), mn, mx)


def update_config(existing_config, new_config):
    for key, value in new_config.items():
        if isinstance(value, collections.abc.Mapping):
            existing_config[key] = update_config(existing_config.get(key, {}), value)
        else:
            existing_config[key] = value
    return existing_config


def get_birth_date(date_created, age):
    start_date = date_created - relativedelta(years=age + 1) + relativedelta(days=1)
    end_date = date_created - relativedelta(years=age)
    ordinal_start_date = start_date.toordinal()
    ordinal_end_date = end_date.toordinal()
    random_ordinal_date = random.randint(ordinal_start_date, ordinal_end_date)
    random_date = date.fromordinal(random_ordinal_date)
    return random_date


def pickle_large_object(obj):
    obj_name = type(obj).__name__ + str(generate_random_digits(5))
    outfile = open(obj_name, "wb")
    joblib.dump(obj, outfile, protocol=3)
    outfile.close()
    return obj_name


def joblib_dumps(obj):
    filename = pickle_large_object(obj)
    with open(filename, "rb") as file:
        obj = file.read()
    os.remove(filename)
    return obj


def make_universe_key(length=10):
    return "".join(random.choice(ascii_lowercase) for _ in range(length))
