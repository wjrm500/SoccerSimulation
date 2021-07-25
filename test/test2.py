import sys
sys.path.append(r"C:\\Users\\Will May\\Documents\\Python\\SoccerSim\\app\\models")
from Database import Database

db = Database.getInstance()
results = db.cnx['soccersim']['forenames'].find()
resultData = [record for record in results]
forenames = [record['forename'] for record in resultData]
forenameWeights = [record['frequency'] for record in resultData]
a = 1