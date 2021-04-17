from Universe import Universe

# def simulate():
    ### Create Universe, taking in input parameters from user

universe = Universe()
universe.timeTravel(300)

import pickle
import random
import string

letters = string.ascii_lowercase
random_string = ''.join(random.choice(letters) for i in range(10))
with open('universe_{}'.format(random_string), 'wb') as outfile:
    pickle.dump(universe, outfile)