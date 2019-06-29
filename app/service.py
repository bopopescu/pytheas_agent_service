from datetime import datetime
from threading import Thread
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances

from app.business_logic import BusinessLogic
from app.data_manager.data_manager_mongo_db import DataManagerMongoDB
from app.data_manager.data_manager_sql import DataManagerSQL


class Service:

    def __init__(self):
        self.date_importer_mongo = DataManagerMongoDB()
        self.bl = BusinessLogic()
        self.date_manager_sql = DataManagerSQL()

    def get_top_attraction_tags(self):
        return self.date_manager_sql.get_top_tags()

    def predict_trip_for_profile(self, profile_id, city_id=None, days=1):
        predictions_result = []
        city_ids = []
        cities_length = 3
        min_attractions_length = days*6
        if city_id is None:
            cities_rates = self.predict_profile_cities_rate(profile_id)
            for i in range(0, cities_length):
                city_ids.append(cities_rates[i][0])
        else:
            city_ids.append(city_id)

        for id in city_ids:
            if len(predictions_result) >= cities_length:
                break
            attractions_vector, att_length = self.predict_attractions_for_profile_city(profile_id, id)
            if att_length >= min_attractions_length:
                predictions_result.append({'city_id': id, 'attractions': attractions_vector})
        return predictions_result

    def predict_attractions_for_profile_city(self, profile_id, city_id):
        profile_city_vector, attractions_length = self.date_manager_sql.get_profile_city_recommendations(profile_id, city_id)
        #profile_city_vector = None
        if profile_city_vector is None or len(profile_city_vector) == 0:
            profiles_prediction_response, attractions_length = self.predict_attractions_for_city(city_id, profile_id)
            profile_city_vector = profiles_prediction_response[profile_id]
        else:
            print("---------=========================loaded vector for profile")

        profile_city_vector = self.bl.dictionary_sort_by_key(profile_city_vector)
        return profile_city_vector, attractions_length

    def predict_attractions_for_city(self, city_id, profile_id=-1):
        global df_profile_ratings
        df_profile_tags, df_profile_ratings, attractions_list = self.date_manager_sql.load_users_attractions_tags(city_id, profile_id)
        df_attractions_tags = self.date_manager_sql.load_attractions_tags_for_city(city_id)
        df_profile_tags[np.isnan(df_profile_tags)] = 0
        profiles_vector = list(df_profile_ratings.index.values)

        m_predicted = self.calculate_matrix_mf(df_profile_tags, df_profile_ratings, df_attractions_tags,
                                               attractions_list)
        m_predicted_knn = self.calculate_matrix_knn(df_profile_tags, df_profile_ratings, attractions_list)

        m_predicted = self.bl.union_prediction_matrixes(m_predicted, m_predicted_knn)

        attractions_length = 0
        profiles_prediction_response = {}
        for i in range(0, len(profiles_vector)):
            attractions_rates = {}
            for j in range(0, len(attractions_list)):
                rate = int(m_predicted[i][j])
                if rate >= 1:
                    rate_attractions = []
                    if rate in attractions_rates:
                        rate_attractions = attractions_rates[rate]
                    rate_attractions.append(attractions_list[j])
                    attractions_length+=1
                    attractions_rates[rate] = rate_attractions
            profiles_prediction_response[profiles_vector[i]] = attractions_rates

        #Async Store to DB
        #Thread(target=self.store_predictions_to_db, args=(city_id, profiles_prediction_response,)).start()
        return profiles_prediction_response, attractions_length

    def predict_profile_cities_rate(self, profile_id):
        return self.date_manager_sql.get_profile_cities_rate(profile_id)

    def import_initial_attractions_for_city(self, city_name):
        df_users_tags, df_users_ratings, attractions_list = self.date_importer.load_data_from_service(city_name)
        df_users_tags[np.isnan(df_users_tags)] = 0
        self.store_internal_datasets_to_db(df_users_tags, df_users_ratings)

    def calculate_matrix_knn(self, df_users_tags, df_users_ratings, attractions_list):
        start_time = datetime.now()

        df_users_tags_calced = self.bl.calculate_user_tags_matrix(df_users_tags)
        df_users_ratings_calced, sparsity = self.bl.calculate_user_ratings_matrix(df_users_ratings, attractions_list)
        df_users_ratings_calced_centered, mean_point = self.bl.center_matrix(df_users_ratings_calced)

        m_similarity = pairwise_distances(df_users_tags_calced, metric='cosine')
        m_predicted = self.bl.predict_knn(df_users_ratings_calced_centered, m_similarity, mean_point, type='user')

        end_time = datetime.now()

        self.bl.calculate_error_rate(df_users_ratings_calced, m_predicted)
        total_time = end_time - start_time
        print('Total Calc Time: {:4.2f}'.format(total_time.total_seconds()))

        return m_predicted

    def calculate_matrix_mf(self, df_users_tags, df_users_ratings, df_attractions_tags, attractions_list):
        try:
            start_time = datetime.now()

            user_tag_matrix = np.array(df_users_tags)
            tag_attraction_matrix = np.array(df_attractions_tags)
            rating_matrix, sparsity = self.bl.calculate_user_ratings_matrix(df_users_ratings, attractions_list)

            r = rating_matrix
            p = user_tag_matrix
            q = tag_attraction_matrix
            k = len(tag_attraction_matrix)

            m_np, m_nq = self.bl.matrix_factorization(r, p, q, k)
            m_predicted = np.dot(m_np, m_nq.T)

            end_time = datetime.now()

            m_predicted = self.bl.round_matrix(m_predicted)
            self.bl.calculate_error_rate(rating_matrix, m_predicted)

            total_time = end_time - start_time
            print('Total Calc Time: {:4.2f}'.format(total_time.total_seconds()))

            return m_predicted
        except Exception as e:
            print(e)

    def store_internal_datasets_to_db(self, df_users_tags, df_users_ratings):
        for user_name, tags_row in df_users_tags.iterrows():
            self.date_manager_sql.insert_internal_user(user_name)
            for i in range(0, len(tags_row)):
                if tags_row[i] > 0:
                    self.date_manager_sql.insert_tag_for_internal_user(user_name, df_users_tags.columns[i])

        for user_name, ratings_row in df_users_ratings.iterrows():
            for i in range(0, len(ratings_row)):
                if ratings_row[i] is not None:
                    att_name = ratings_row[i][0]
                    att_rating = ratings_row[i][1]
                    self.date_manager_sql.insert_ratings_for_internal_user(user_name, att_name, att_rating)

    def store_predictions_to_db(self, city_id, profiles_prediction):
        for profile_id in profiles_prediction:
            #if profile_id in (1,2):
            print("start saving for - " + str(profile_id))
            self.date_manager_sql.insert_profile_prediction(profile_id, city_id, profiles_prediction[profile_id])
            print("finished saving for - " + str(profile_id))
        self.date_manager_sql.migrate_city_predictions(city_id)

'''
if __name__ == '__main__':
    agent_service = Service();
    #resX = agent_service.get_top_attraction_tags()
    resX = agent_service.predict_trip_for_profile(17278, 11)
    #resX = agent_service.predict_profile_cities_rate(22)
    #resX= agent_service.predict_attractions_for_city(11)
    print(resX)
'''
