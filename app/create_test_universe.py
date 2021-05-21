import sys
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app\\models")
from Universe import Universe

# def simulate():
    ### Create Universe, taking in input parameters from user

systemIds = [2]

universe = Universe(systemIds = systemIds)
universe.timeTravel(325)

import pickle
import random
import string

letters = string.ascii_lowercase
random_string = ''.join(random.choice(letters) for i in range(10))
with open('universe_{}'.format(random_string), 'wb') as outfile:
    pickle.dump(universe, outfile)