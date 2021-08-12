from ss.models.Database import Database
from datetime import datetime, timedelta
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, To, Email, Content

db = Database.getInstance()
my_client = db.cnx
my_db = my_client['grid_file']
files = my_db['fs.files']
chunks = my_db['fs.chunks']

deletion_threshold = datetime.now() - timedelta(hours = 12)
query = {'uploadDate': {'$lt': deletion_threshold}}
results = list(files.find(query))
file_ids_to_delete = [i['_id'] for i in results]
total_bytes_to_delete = sum([i['length'] for i in results])

deleted_files = files.delete_many(query)
deleted_chunks = chunks.delete_many({'files_id': {'$in': file_ids_to_delete}})

if deleted_files.deleted_count > 0:
    from_email = Email('therealsoccersim@gmail.com')
    to_email = To('wjrm500@gmail.com')
    subject = 'Soccer Simulation MongoDB notice - {} files deleted'.format(deleted_files.deleted_count)
    content = Content('text/html', '{} files and {} chunks were just removed from your MongoDB instance (a total of {} bytes).'.format(
            deleted_files.deleted_count,
            deleted_chunks.deleted_count,
            total_bytes_to_delete
        )
    )
    message = Mail(from_email, to_email, subject, content)
    try:
        sg = SendGridAPIClient(api_key = os.environ.get('SENDGRID_API_KEY'))
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)