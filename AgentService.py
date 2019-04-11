import DataImporter
import AgentBL
import numpy as np
from sklearn.metrics.pairwise import pairwise_distances
from datetime import datetime


class AgentService:

    def __init__(self):
        self.date_importer = DataImporter.DataManagerMongo()
        self.bl = AgentBL.AgentServiceBL()

    def calculate_matrix_for_city(self, city_name):
        df_users_tags, df_users_ratings, attractions_list = self.date_importer.load_data_from_service(city_name)
        df_users_tags[np.isnan(df_users_tags)] = 0

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
        # insert to DB
        return m_predicted;


if __name__ == '__main__':
    print('start')
    agent_service = AgentService();
    result = agent_service.calculate_matrix_for_city('paris')
    print('end')

