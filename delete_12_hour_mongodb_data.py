from datetime import datetime, timedelta

from ss.email_service import EmailService
from ss.models.Database import Database

db = Database.get_instance()
my_client = db.cnx
my_db = my_client["grid_file"]
files = my_db["fs.files"]
chunks = my_db["fs.chunks"]

deletion_threshold = datetime.now() - timedelta(hours=12)
query = {"uploadDate": {"$lt": deletion_threshold}}
results = list(files.find(query))
file_ids_to_delete = [i["_id"] for i in results]
total_bytes_to_delete = sum([i["length"] for i in results])

deleted_files = files.delete_many(query)
deleted_chunks = chunks.delete_many({"files_id": {"$in": file_ids_to_delete}})

if deleted_files.deleted_count > 0:
    email_service = EmailService()
    email_service.send_mongodb_deletion_notification(
        deleted_files.deleted_count, deleted_chunks.deleted_count, total_bytes_to_delete
    )
