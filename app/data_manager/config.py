
class Config:
    def __init__(self):
        #self.mongoURL = "mongodb://test11:test11@ds215633.mlab.com:15633/pytheas"
        self.mongo_url = "mongodb://test11:test11@ds215633.mlab.com:15633/pytheas"
        self.mongo_db_name = 'pytheas'
        self.USERNAME = 'pytheas'
        self.PASSWORD = 'TravelMaker1'
        self.HOST = '35.240.98.26'
        self.DATABASE_NAME = 'pytheas'
        self.CONNECTION_NAME = 'sigma-chemist-235920:europe-west1:pytheas-app'
        self.DB_URI = 'mysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE_NAME}'
