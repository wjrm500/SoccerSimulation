import os

import mysql.connector

from ss.models.Database import Database

cnx = mysql.connector.connect(
    user=os.environ.get("MYSQL_USER"),
    password=os.environ.get("MYSQL_PWD"),
    host="127.0.0.1",
    database=os.environ.get("MYSQL_DB"),
)
cursor = cnx.cursor()

db = Database.get_instance()
cnx = db.cnx["soccersim"]

firstname_sql = "SELECT `firstname`, `count`, `frequency` FROM `firstnames`"
cursor.execute(firstname_sql)
results = cursor.fetchall()
forename_collection = cnx["forenames"]
for i, result in enumerate(results, 1):
    forename_collection.insert_one(
        {"_id": i, "forename": result[0], "count": result[1], "frequency": result[2]}
    )

surname_sql = "SELECT `surname`, `count`, `frequency` FROM `surnames`"
cursor.execute(surname_sql)
results = cursor.fetchall()
surname_collection = cnx["surnames"]
for i, result in enumerate(results, 1):
    surname_collection.insert_one(
        {"_id": i, "surname": result[0], "count": result[1], "frequency": result[2]}
    )

city_sql = "SELECT `system_id`, `city_name` FROM `city`"
cursor.execute(city_sql)
results = cursor.fetchall()
city_collection = cnx["cities"]
for i, result in enumerate(results, 1):
    city_collection.insert_one({"_id": i, "system_id": result[0], "city_name": result[1]})

system_sql = "SELECT `system_name` FROM `system`"
cursor.execute(system_sql)
results = cursor.fetchall()
system_collection = cnx["systems"]
for i, result in enumerate(results, 1):
    system_collection.insert_one({"_id": i, "system_name": result[0]})
