import random
import string
import collections.abc
import numpy as np
import random
from datetime import date
from dateutil.relativedelta import relativedelta
import copy
import pickle
import glob
import os
import re
import joblib
from .models.Database import Database

def generateName(chars):        
    return ''.join(random.choice(string.ascii_lowercase) for _ in range(chars))

def loadPlayerNames():
    db = Database.getInstance()
    results = db.cnx['soccersim']['forenames'].find()
    results = [record for record in results]
    global forenames, forenameWeights
    forenames = [record['forename'] for record in results]
    forenameCounts = [record['count'] for record in results]
    countSum = sum(forenameCounts)
    forenameWeights = [record['count'] / countSum for record in results]

    results = db.cnx['soccersim']['surnames'].find()
    results = [record for record in results]
    global surnames, surnameWeights
    surnames = [record['surname'] for record in results]
    surnameCounts = [record['count'] for record in results]
    countSum = sum(surnameCounts)
    surnameWeights = [record['count'] / countSum for record in results]

def sortMcAndOApostrophe(name):
    rx = re.compile(r'(?:(?<=Mc)|(?<=O\'))([a-z])')
    def repl(m):
        char = m.group(1)
        return char.upper()
    return rx.sub(repl, name)

def generatePlayerName():
    if 'forenames' not in globals():
        loadPlayerNames()
    forename = np.random.choice(forenames, p = forenameWeights)
    surname = np.random.choice(surnames, p = surnameWeights)
    surname = sortMcAndOApostrophe(surname)
    return (forename, surname)

def generateRandomDigits(n):
    return ''.join(random.choice(string.digits) for _ in range(n))

def limitValue(value, mn = None, mx = None):
    if mn is not None:
        if value < mn:
            return mn
    if mx is not None:
        if value > mx:
            return mx
    return value

def limitedRandNorm(dictionary):
    [mu, sigma, mn, mx] = [value for value in list(dictionary.values())]
    return limitValue(np.random.normal(mu, sigma), mn, mx)

def updateConfig(existingConfig, newConfig):
    for key, value in newConfig.items():
        if isinstance(value, collections.abc.Mapping):
            existingConfig[key] = updateConfig(existingConfig.get(key, {}), value)
        else:
            existingConfig[key] = value
    return existingConfig

def getBirthDate(dateCreated, age):
    startDate = dateCreated - relativedelta(years = age + 1) + relativedelta(days = 1)
    endDate = dateCreated - relativedelta(years = age)
    ordinalStartDate = startDate.toordinal()
    ordinalEndDate = endDate.toordinal()
    randomOrdinalDate = random.randint(ordinalStartDate, ordinalEndDate)
    randomDate = date.fromordinal(randomOrdinalDate)
    return randomDate

def typeAgnosticOmit(dictionary, omittedKeys):
    """Omits given keys from dictionary."""
    output = copy.deepcopy(dictionary)
    omittedKeys = omittedKeys if type(omittedKeys) == list else [omittedKeys]
    for omittedKey in omittedKeys:
        try:
            del output[omittedKey]
        except:
            continue
    return output

def pickleObject(obj):
    objName = type(obj).__name__ + str(generateRandomDigits(5))
    outfile = open(objName, 'wb')
    pickle.dump(obj, outfile)
    outfile.close()

def pickleLargeObject(obj):
    objName = type(obj).__name__ + str(generateRandomDigits(5))
    outfile = open(objName, 'wb')
    joblib.dump(obj, outfile)
    outfile.close()

def unpickleMostRecent(path):
    files = glob.glob(path + '/*')
    latestPickleFileName = max(files, key = os.path.getctime)
    latestPickle = open(latestPickleFileName, 'rb')
    latestPickleUnpickled = pickle.load(latestPickle)
    latestPickle.close()
    return latestPickleUnpickled

def getAllPowersOfTwoLessThan(n): 
    results = []; 
    for i in range(n, 0, -1): 
        if ((i & (i - 1)) == 0): 
            results.append(i); 
    return results

def getHighestPowerOfTwoLessThan(n): 
    result = 0; 
    for i in range(n, 0, -1): 
        if ((i & (i - 1)) == 0): 
            result = i
            break 
    return result

def printCodeTimeTaken(code):
    global datetimeNow
    global datetimePrevious
    datetimeNow = datetime.now()
    if 'datetimePrevious' in globals():
        timeTaken = datetimeNow - datetimePrevious
    else:
        timeTaken = 0
    print('Code: {} --- Time taken: {}'.format(code, timeTaken))
    datetimePrevious = datetimeNow