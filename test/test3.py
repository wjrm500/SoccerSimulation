import sys
sys.path.append('.')
import ss.utils as utils
import pickle

d = {
    'a': 1,
    'b': 2
}

print(utils.joblibDumps(d))
print(pickle.dumps(d))