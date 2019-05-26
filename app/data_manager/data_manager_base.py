from abc import ABC, abstractmethod


class DataManagerBase(ABC):
    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    def load_users_attractions_tags(self, city):
        raise Exception("NotImplementedException")
