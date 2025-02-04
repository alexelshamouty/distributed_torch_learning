from common.ports.messaging_ports import MessagingPort
import oslo_messaging

class OsloMessaging(MessagingPort):
    def __init__(self, transport: oslo_messaging.transport.Transport):
        # Send the job to the selected worker topic
        self.client = None
        self.transport = transport
        self.target = None

    def get_client(self, target):
        self.target = target
        self.client = oslo_messaging.get_rpc_client(self.transport, target=target)
        return self.client
    
    def call_block(self,context, message):
        print(f"Sending message: {message}")

    def cast_async(self,context, message):
        print(f"Casting message: {message}")
