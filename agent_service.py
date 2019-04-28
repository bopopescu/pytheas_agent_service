import data_manager_mongo_db
import data_manager_sql
import agent_business_logic
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from datetime import datetime


class AgentService:

    def __init__(self):
        self.date_importer = data_manager_mongo_db.DataManagerMongoDB();
        self.bl = agent_business_logic.AgentServiceBL();
        self.date_importer_sql = data_manager_sql.DataManagerSQL();

    def predict_initial_attractions_for_city(self, city_name):
        df_users_tags, df_users_ratings, attractions_list = self.date_importer.load_data_from_service(city_name)
        df_users_tags[np.isnan(df_users_tags)] = 0

        m_predicted = self.calculate_matrix(df_users_tags, df_users_ratings, attractions_list)
        return m_predicted;

    def predict_attractions_for_city(self, city_name):
        df_users_tags, df_users_ratings, attractions_list = self.date_importer_sql.load_data_from_db(city_name)
        df_users_tags[np.isnan(df_users_tags)] = 0

        m_predicted = self.calculate_matrix(df_users_tags, df_users_ratings, attractions_list)
        return m_predicted;

    def calculate_matrix(self, df_users_tags, df_users_ratings, attractions_list):
        start_time = datetime.now()

        df_users_tags_calced = self.bl.calculate_user_tags_matrix(df_users_tags)
        df_users_tags_calced_centered, ignore = self.bl.center_matrix(df_users_tags_calced)

        df_users_ratings_calced = self.bl.calculate_user_ratings_matrix(df_users_ratings, attractions_list)
        df_users_ratings_calced_Centered, mean_point = self.bl.center_matrix(df_users_ratings_calced)

        # m_similarity = self.bl.fast_similarity(df_users_tags_calced_centered, 'user')
        m_similarity = pairwise_distances(df_users_tags_calced_centered, metric='cosine')
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

    def store_datasets_to_db(self):

        for user_name, tags_row in self.df_users_tags.iterrows():
            # store users
            print(user_name)
            self.date_importer_sql.insert_internal_user(user_name)
            for i in range(0, len(tags_row)):
                if (tags_row[i] > 0):
                    print(self.df_users_tags.columns[i])
                    # store user tags
                    self.date_importer_sql.insert_tag_for_internal_user(user_name, self.df_users_tags.columns[i])

        for user_name, ratings_row in self.df_users_ratings.iterrows():
            for i in range(0, len(ratings_row)):
                if (ratings_row[i] != None):
                    att_name = ratings_row[i][0]
                    att_rating = ratings_row[i][1]
                    # print(self.df_users_ratings.columns[i])
                    # store user tags
                    self.date_importer_sql.insert_ratings_for_internal_user(user_name, att_name, att_rating)


if __name__ == '__main__':
    agent_service = AgentService();
    result = agent_service.predict_attractions_for_city('paris')
    # agent_service.store_datasets_to_db()
    # save to db

