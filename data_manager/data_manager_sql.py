import operator

import mysql.connector
import pandas as pn
import numpy as np

import config
from data_manager.data_manager_base import DataManagerBase


class DataManagerSQL(DataManagerBase):

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

    def insert_profile_prediction(self, profile_id, city_id, attractions_rates):
        global rates_attractions
        rates_attractions = {}
        for attraction_name in attractions_rates:
            rate = attractions_rates[attraction_name]
            rate_attractions = ''
            if rate in rates_attractions.keys():
                rate_attractions = rates_attractions[rate]
            rate_attractions += "'" + attraction_name.replace("'", "''") + "',"
            rates_attractions[rate] = rate_attractions

        for rate in rates_attractions:
            attractions = rates_attractions[rate][:-1]
            print(rate)
            print(attractions)
            self.run_stored_procedure("pytheas.add_profile_attractions_prediction",
                                      [int(profile_id), attractions, float(rate)])

    def insert_profile_attraction_prediction(self, profile_id, city_id, attractions_rates, attraction_name):
        print('running ' + attraction_name)
        self.run_stored_procedure("pytheas.add_profile_attraction_prediction",
                                  [int(profile_id), int(city_id), attraction_name,
                                   float(attractions_rates[attraction_name])])

    def migrate_city_predictions(self, city_id):
        self.run_stored_procedure("pytheas.migrate_profiles_attractions_predictions", [city_id])

    # overriding abstract method
    def load_users_attractions_tags(self, city_id):
        profiles_ratings_db = []
        profiles_tags_db = []

        profiles_ratings = {}
        profiles_tags = {}

        attractions = []
        df_users_tags = []
        df_users_ratings = []

        att_results = self.run_stored_procedure("pytheas.get_attractions_by_city", [city_id])
        for result in att_results:
            attractions_list_result = result.fetchall()
            for att in attractions_list_result:
                attractions.append(att[0])

        profiles_ratings_db_results = self.run_stored_procedure("pytheas.get_all_profiles_ratings", [city_id])
        for result in profiles_ratings_db_results:
            profiles_ratings_db = result.fetchall()

        profiles_tags_db_results = self.run_stored_procedure("pytheas.get_all_profiles_tags_by_city", [city_id])
        for result in profiles_tags_db_results:
            profiles_tags_db = result.fetchall()

        for row in profiles_ratings_db:
            profile_id = row[0]
            # attraction_id = row[1]
            attraction_name = row[2]
            rate = row[3]

            profile_attractions = []
            if profile_id in profiles_ratings.keys():
                profile_attractions = profiles_ratings[profile_id]

            if profile_attractions is None:
                profile_attractions = []
            profile_attractions.append([attraction_name, rate])
            profiles_ratings[profile_id] = profile_attractions

        for row in profiles_tags_db:
            profile_id = row[0]
            tag_id = row[1]
            # tag_value = row[2]

            profile_tags = {}
            if profile_id in profiles_tags.keys():
                profile_tags = profiles_tags[profile_id]

            profile_tags[tag_id] = 1
            profiles_tags[profile_id] = profile_tags

        df_users_ratings = pn.DataFrame.from_dict(profiles_ratings, orient='index')
        df_users_ratings.sort_index(inplace=True)
        df_users_ratings.insert(0, '_ID', range(0, 0 + len(df_users_ratings)))

        df_users_tags = pn.DataFrame.from_dict(profiles_tags, orient='index')
        df_users_tags.sort_index(inplace=True)
        return df_users_tags, df_users_ratings, attractions

    def load_attractions_tags_for_city(self, city_id):
        tags_attractions = {}
        att_results = self.run_stored_procedure("pytheas.get_attractions_tags_by_city", [city_id])
        for result in att_results:
            attractions_list_result = result.fetchall()
            for att in attractions_list_result:
                attraction_id = att[0]
                tag_id = att[1]
                avg_rate = att[2]

                att_tags = tags_attractions.get(tag_id)
                if att_tags is None:
                    att_tags = {}
                if attraction_id not in att_tags:
                    att_tags[attraction_id] = 0
                att_tags[attraction_id] = avg_rate
                tags_attractions[tag_id] = att_tags

        df_attractions_tags = pn.DataFrame.from_dict(tags_attractions, orient='index')
        df_attractions_tags = df_attractions_tags.reindex(sorted(df_attractions_tags.columns), axis=1)
        df_attractions_tags.sort_index(inplace=True)
        df_attractions_tags[np.isnan(df_attractions_tags)] = 0
        return df_attractions_tags

    def get_profile_rate_for_city(self, profile_id, city_id):
        return_value = 0
        db_results = self.run_stored_procedure("pytheas.get_profile_rate_for_city", [profile_id, city_id])
        for result in db_results:
            return_value = result.fetchall()
        return float(return_value[0][0])

    def get_profile_city_recommendations(self, profile_id, city_id):
        profile_vector = []
        predictions_list = []
        db_results = self.run_stored_procedure("pytheas.get_profile_attractions_prediction", [profile_id, city_id])
        for result in db_results:
            predictions_list = result.fetchall()
        for attraction_id, rate in predictions_list:
            attraction_rate = {'attraction_id': attraction_id, 'rate': rate}
            profile_vector.append(attraction_rate)
        return profile_vector

    def get_profile_cities_rate(self, profile_id):
        cities_list = []
        cities_ratings = {}
        db_results = self.run_stored_procedure("pytheas.get_all_cities", [])
        for result in db_results:
            cities_list = result.fetchall()

        for city_id, city_name in cities_list:
            cities_ratings[city_id] = self.get_profile_rate_for_city(profile_id, city_id)
        return sorted(cities_ratings.items(), key=operator.itemgetter(1), reverse=True)

    def insert_to_db(self, query):
        print(query)
        self.cursor.execute(query)
        self.db_client.commit()

    def run_stored_procedure(self, procedure_name, args):
        print(procedure_name)
        print(args)
        self.cursor.callproc(procedure_name, args)
        self.db_client.commit()
        return self.cursor.stored_results()
