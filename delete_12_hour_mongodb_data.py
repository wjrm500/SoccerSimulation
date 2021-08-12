from ss.models.Database import Database
from datetime import datetime, timedelta

db = Database.getInstance()
my_client = db.cnx
my_db = my_client['grid_file']
files = my_db['fs.files']
deletion_threshold = datetime.now() - timedelta(hours = 12)
query = {"uploadDate": {"$lt": deletion_threshold}}
x = files.delete_many(query)
print('{} documents deleted'.format(x.deleted_count))