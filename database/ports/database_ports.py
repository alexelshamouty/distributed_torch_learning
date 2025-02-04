from abc import ABC, abstractmethod

class DatabasePort(ABC):
    @staticmethod
    @abstractmethod
    def get_engine(self):
        pass

    @staticmethod
    @abstractmethod
    def get_session(self):
        pass
    @staticmethod
    @abstractmethod 
    def init_db(self):
        pass