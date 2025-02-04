from abc import ABC, abstractmethod

class DatabasePort(ABC):
    @abstractmethod
    def get_engine(self):
        pass

    
    @abstractmethod
    def get_session(self, sql):
        pass
    
    @abstractmethod 
    def get_all_nodes(self):
        pass
    
    @abstractmethod
    def close(self):
        pass
