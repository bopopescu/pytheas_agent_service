import mysql.connector
from mysql.connector import Error

import config


class DataManagerSQL:

    def _init_(self):

        self.db_client = mysql.connector.connect(
            host=config.HOST,
            database=config.DATABASE_NAME,
            user=config.USERNAME,
            password=config.PASSWORD
        )
        self.cursor = self.db_client.cursor()

    def insert_internal_user(self, user_name):
        query = "INSERT INTO pytheas.agent_internal_users (username, create_time) VALUES ('" + user_name + "', UTC_TIMESTAMP());"
        self.insert_to_db(query)

    def insert_tags_for_internal_user(self, user_name, tags):
        for tag in tags:
            query = "INSERT INTO `pytheas`.`agent_internal_users_tags` VALUES ('" + user_name + "', '" + tag + "')"
            self.insert_to_db(query)

    def insert_ratings_for_internal_user(self, user_name, attractions):
        for attraction in attractions:
            query = "INSERT INTO `pytheas`.`agent_internal_users_tags` VALUES ('" + user_name;
            query += "', 'empty', '" + attraction['name'] + "', '" + attraction['rate'] + "')"
            self.insert_to_db(query)

    def insert_to_db(self, query):
        print(query)
        self.cursor.execute(query)
        self.db_client.commit()


#_db = DataManagerSQL();
# response = _db.load_attraction_for_city();
#resi1 = _db.insert_internal_user("userName")