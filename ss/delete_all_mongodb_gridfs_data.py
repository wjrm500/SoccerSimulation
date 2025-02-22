from models.Database import Database

db = Database.get_instance()
my_client = db.cnx
my_db = my_client["grid_file"]
chunks = my_db["fs.chunks"]
print(chunks.count_documents({}))
files = my_db["fs.files"]
print(files.count_documents({}))
x = chunks.delete_many({})
y = files.delete_many({})
print(x, y)
