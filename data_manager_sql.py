import mysql.connector
import pandas as pn
import operator

import config
from data_manager_base import DataManageBase


class DataManagerSQL(DataManageBase):

    def __init__(self):

        self.db_client = mysql.connector.connect(
            host=config.HOST,
            database=config.DATABASE_NAME,
            user=config.USERNAME,
            password=config.PASSWORD
        )
        self.cursor = self.db_client.cursor()

    def insert_internal_user(self, user_name):
        user_name = user_name + '_agent_user'
        sp_results = self.run_stored_procedure("pytheas.add_internal_user", [user_name])
        for result in sp_results:
            return result.fetchall()[0][0]

    def insert_tag_for_internal_user(self, user_name, tag):
        user_name = user_name + '_agent_user'
        self.run_stored_procedure("pytheas.add_internal_user_tag", [user_name, tag])

    def insert_ratings_for_internal_user(self, user_name, attraction_name, rate):
        user_name = user_name + '_agent_user'
        self.run_stored_procedure("pytheas.add_internal_user_attraction", [user_name, attraction_name, rate])

    # overriding abstract method
    def load_users_attractions_tags(self, city_name):

        df_users_tags = []
        df_users_ratings = []
        attractions_list = []

        users = []
        users_tags = {}
        users_ratings = {}

        att_results = self.run_stored_procedure("pytheas.get_attractions_by_city", [city_name])
        for result in att_results:
            attractions_list_result = result.fetchall()
            for att in attractions_list_result:
                attractions_list.append(att[0])

        users_results = self.run_stored_procedure("pytheas.get_users_by_city", [city_name])
        for result in users_results:
            users = result.fetchall()
            for row in users:
                # get user tags
                user_tags = {}
                user_tags_results = self.run_stored_procedure("pytheas.get_user_tags", [row[0]])
                for result in user_tags_results:
                    fetched_results = result.fetchall()
                    for user_tag in fetched_results:
                        user_tags[user_tag[1]] = 1
                users_tags[row[1]] = user_tags

                # get user rates
                attractions = []
                user_ratings_results = self.run_stored_procedure("pytheas.get_user_ratings", [row[0]])
                for result in user_ratings_results:
                    fetched_results = result.fetchall()
                    for user_rating in fetched_results:
                        attractions.append([user_rating[1], user_rating[2]])
                users_ratings[row[1]] = attractions

        df_users_ratings = pn.DataFrame.from_dict(users_ratings, orient='index')
        df_users_ratings.sort_index(inplace=True)
        df_users_ratings.insert(0, '_ID', range(0, 0 + len(df_users_ratings)))

        df_users_tags = pn.DataFrame.from_dict(users_tags, orient='index')
        df_users_tags.sort_index(inplace=True)
        return df_users_tags, df_users_ratings, attractions_list;

    def get_profile_rate_for_city(self, profile_id, city_id):
        return_value = 0
        db_results = self.run_stored_procedure("pytheas.get_profile_rate_for_city", [profile_id, city_id])
        for result in db_results:
            return_value = result.fetchall()
        return float(return_value[0][0]);

    def get_all_cities(self):
        cities_list = []
        db_results = self.run_stored_procedure("pytheas.get_all_cities", [])
        for result in db_results:
            cities_list = result.fetchall()
        return cities_list

    def get_profile_cities_rate(self, profile_id):
        cities_ratings = {}

        cities_list = self.get_all_cities();
        for city_id, city_name in cities_list:
            cities_ratings[city_id] = self.get_profile_rate_for_city(profile_id, city_id)
        return sorted(cities_ratings.items(), key=operator.itemgetter(1), reverse=True)

    def insert_to_db(self, query):
        print(query)
        self.cursor.execute(query)
        self.db_client.commit()

    def run_stored_procedure(self, procedur_name, args):
        print(procedur_name)
        print(args)
        self.cursor.callproc(procedur_name, args)
        self.db_client.commit()
        return self.cursor.stored_results()

# _db = DataManagerSQL();
# response1, response2, response3 = _db.load_data_from_DB('paris');
# resi1 =  _db.insert_internal_user('fsgdsfdg')
# print(resi1)
