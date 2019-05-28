from abc import ABC, abstractmethod
import os

if 'HEROKU' in os.environ:
    from app.data_manager import heroku_config as config
else:
    from app.data_manager import config

class DataManagerBase(ABC):
    @abstractmethod
    def __init__(self):
        self.config = config

    @abstractmethod
    def load_users_attractions_tags(self, city):
        raise Exception("NotImplementedException")
