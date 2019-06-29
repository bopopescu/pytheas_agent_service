import os

mongoURL = "mongodb://test11:test11@ds215633.mlab.com:15633/pytheas"
mongo_url = "mongodb://test11:test11@ds215633.mlab.com:15633/pytheas"
mongo_db_name = 'pytheas'

USERNAME = os.environ.get('DB_USERNAME')
PASSWORD = os.environ.get('DB_PASSWORD')
HOST = os.environ.get('DB_HOST')
DATABASE_NAME = 'pytheas'

DB_URI = 'mysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}'