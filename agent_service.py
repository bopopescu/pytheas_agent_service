import data_manager_mongo_db
import data_manager_sql
import agent_business_logic
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from datetime import datetime


class AgentService:

    def __init__(self):
        self.date_importer_mongo = data_manager_mongo_db.DataManagerMongoDB();
        self.bl = agent_business_logic.AgentServiceBL();
        self.date_importer_sql = data_manager_sql.DataManagerSQL();

    def predict_trip_for_profile(self, profile_id, city_id):
        predictions_result = []
        city_ids = []
        city_id = 11  # paris
        if (city_id is None):
            cities_length = 3
            cities_rates = self.predict_profile_cities_rate(profile_id)
            if (len(cities_rates) < 3): cities_length = len(cities_rates)
            for i in range(0, cities_length):
                city_ids.append(cities_rates[i][0])
        else:
            city_ids.append(city_id)

        for id in city_ids:
            attractions_vector = self.predict_attractions_for_profile_city(profile_id, id)
            predictions_result.append({'city_id': city_id, 'attractions': attractions_vector})
        return predictions_result;

    def predict_attractions_for_profile_city(self, profile_id, city_id):
        profile_city_vector = []

        profile_city_vector = self.date_importer_sql.get_profile_city_recommendations(profile_id, city_id)
        print(profile_city_vector);
        if profile_city_vector is None or len(profile_city_vector) == 0:
            self.predict_attractions_for_city(city_id)
            profile_city_vector = self.date_importer_sql.get_profile_city_recommendations(profile_id, city_id)
        return profile_city_vector

    def predict_attractions_for_city(self, city_id):
        df_profile_tags, df_profile_ratings, attractions_list = self.date_importer_sql.load_users_attractions_tags(city_id)
        df_profile_tags[np.isnan(df_profile_tags)] = 0
        profiles_vector = list(df_profile_ratings.index.values)
        m_predicted = self.calculate_matrix(df_profile_tags, df_profile_ratings, attractions_list)

        profiles_prediction_response = {}
        for i in range(0, len(profiles_vector)):
            attractions_rates = {}
            for j in range(0, len(attractions_list)):
                attractions_rates[attractions_list[j]] = float(format(m_predicted[i][j], '.2f'))
            profiles_prediction_response[profiles_vector[i]] = attractions_rates

        self.store_predictions_to_db(city_id, profiles_prediction_response)
        return profiles_prediction_response

    def predict_profile_cities_rate(self, profile_id):
        return self.date_importer_sql.get_profile_cities_rate(profile_id)

    def predict_initial_attractions_for_city(self, city_name):
        df_users_tags, df_users_ratings, attractions_list = self.date_importer_mongo.load_users_attractions_tags(city_name)
        df_users_tags[np.isnan(df_users_tags)] = 0
        m_predicted = self.calculate_matrix(df_users_tags, df_users_ratings, attractions_list)

        self.store_internal_datasets_to_db(df_users_tags, df_users_ratings);
        return m_predicted;

    def calculate_matrix(self, df_users_tags, df_users_ratings, attractions_list):
        start_time = datetime.now()

        df_users_tags_calced = self.bl.calculate_user_tags_matrix(df_users_tags)
        # df_users_tags_calced_centered, ignore = self.bl.center_matrix(df_users_tags_calced)

        df_users_ratings_calced = self.bl.calculate_user_ratings_matrix(df_users_ratings, attractions_list)
        df_users_ratings_calced_Centered, mean_point = self.bl.center_matrix(df_users_ratings_calced)

        # m_similarity = self.bl.fast_similarity(df_users_tags_calced_centered, 'user')
        m_similarity = pairwise_distances(df_users_tags_calced, metric='cosine')
        m_predicted = self.bl.predict(df_users_ratings_calced_Centered, m_similarity, mean_point, type='user')

        end_time = datetime.now()

        self.bl.calculate_error_rate(df_users_ratings_calced, m_predicted)

        total_time = end_time - start_time

        print('Total Calc Time: {:4.2f}'.format(total_time.total_seconds()))

        self.df_users_tags = df_users_tags
        self.df_users_ratings = df_users_ratings
        self.attractions_list = attractions_list
        self.mean_point = mean_point
        self.similarity = m_similarity
        self.user_ratings = df_users_ratings_calced_Centered
        self.m_predicted = m_predicted

        return m_predicted

    def store_internal_datasets_to_db(self, df_users_tags, df_users_ratings):
        for user_name, tags_row in df_users_tags.iterrows():
            # store users
            print(user_name)
            self.date_importer_sql.insert_internal_user(user_name)
            for i in range(0, len(tags_row)):
                if (tags_row[i] > 0):
                    print(df_users_tags.columns[i])
                    # store user tags
                    self.date_importer_sql.insert_tag_for_internal_user(user_name, df_users_tags.columns[i])

        for user_name, ratings_row in df_users_ratings.iterrows():
            for i in range(0, len(ratings_row)):
                if (ratings_row[i] != None):
                    att_name = ratings_row[i][0]
                    att_rating = ratings_row[i][1]
                    self.date_importer_sql.insert_ratings_for_internal_user(user_name, att_name, att_rating)

    def store_predictions_to_db(self, city_id, profiles_prediction):
        # print(profiles_prediction)
        for profile_id in profiles_prediction:
            self.date_importer_sql.insert_profile_prediction(profile_id, city_id, profiles_prediction[profile_id])
        self.date_importer_sql.migrate_city_predictions(city_id)


if __name__ == '__main__':
    agent_service = AgentService();
    #resX = agent_service.predict_profile_cities_rate(22)
    #resX = agent_service.predict_profile_cities_rate(22)
    resX= agent_service.predict_attractions_for_city(11)
    print(resX)

