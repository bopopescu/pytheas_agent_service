import json

import pandas as pn
from bson import json_util
from pymongo import MongoClient

import config
from app.data_manager.data_manager_base import DataManagerBase


class DataManagerMongoDB(DataManagerBase):

    def __init__(self):

        self.connect_timeout_ms = 30000
        self.mongo_url = config.mongo_url
        self.client = MongoClient(self.mongo_url, connectTimeoutMS=self.connect_timeout_ms)
        self.db = self.client.get_database("pytheas")
        self.collection = self.db.comments_test  # Paris only, for now

    def insert_new_users_and_tags(self):
        mongo_response_documents = self.collection.find({})  # .limit(5)
        json_documents = json.loads(json_util.dumps(mongo_response_documents))

        reviwers_tags = {}
        attractions_list = []

        for i in range(0, len(json_documents)):
            att_id = json_documents[i]['_id']['$oid']
            json_documents[i]['_id'] = att_id
            attractions_list.append(att_id)

        for row in json_documents:
            tags = row['tags']
            for review in row['reviews']['reviews']:
                rev = review['reviewer']
                rate = review['rate']

                user_tags = reviwers_tags.get(rev)
                if user_tags is None:
                    user_tags = {}
                if rate > 0:
                    for tag in tags:
                        if tag not in user_tags:
                            user_tags[tag] = 0
                        user_tags[tag] = 1
                    reviwers_tags[rev] = user_tags

        df_users_tags = pn.DataFrame.from_dict(reviwers_tags, orient='index')
        return df_users_tags

    # overriding abstract method
    def load_users_attractions_tags(self, city_name):
        reviwers = {}
        reviwers_tags = {}
        attractions_list = []

        mongo_response_documents = self.collection.find({})  # .limit(5)
        json_documents = json.loads(json_util.dumps(mongo_response_documents))

        for i in range(0, len(json_documents)):
            att_name = json_documents[i]['name']
            attractions_list.append(att_name)

        for row in json_documents:
            attraction_name = row['name']
            tags = row['tags']
            for review in row['reviews']['reviews']:
                rev = review['reviewer']
                rate = review['rate']

                user_tags = reviwers_tags.get(rev)
                if user_tags is None:
                    user_tags = {}
                if rate > 0:
                    for tag in tags:
                        if tag not in user_tags:
                            user_tags[tag] = 0
                        user_tags[tag] += 1
                    reviwers_tags[rev] = user_tags

                attractions = reviwers.get(rev)
                if attractions is None:
                    attractions = []
                attractions.append([attraction_name, rate])
                reviwers[rev] = attractions

        df_users_ratings = pn.DataFrame.from_dict(reviwers, orient='index')
        df_users_ratings.sort_index(inplace=True)
        df_users_ratings.insert(0, '_ID', range(0, 0 + len(df_users_ratings)))

        df_users_tags = pn.DataFrame.from_dict(reviwers_tags, orient='index')
        df_users_tags.sort_index(inplace=True)

        return df_users_tags, df_users_ratings, attractions_list
