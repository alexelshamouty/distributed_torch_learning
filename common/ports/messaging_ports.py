from abc import ABC, abstractmethod
import oslo_messaging

class MessagingPort(ABC):
    @abstractmethod
    def call_block(self, context, message):
        pass
    @abstractmethod
    def get_client(self, target: str):
        pass
    @abstractmethod
    def cast_async(self, context, message):
        pass