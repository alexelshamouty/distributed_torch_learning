from abc import ABC, abstractmethod

class MessagingPort(ABC):
    @abstractmethod 
    def get_transport(self):
        pass

    @abstractmethod
    def get_rpc_client(self):
        pass