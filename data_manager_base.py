from abc import ABC, abstractmethod


class DataManageBase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def load_users_attractions_tags(self, city_name):
        raise Exception("NotImplementedException")
