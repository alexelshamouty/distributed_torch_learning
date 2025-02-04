from scheduler.ports.scheduler_port import SchedulerPort
from database.ports.database_ports import DatabasePort
from common.ports.messaging import MessagingPort

class FederatedScheduler(SchedulerPort):
    def __init__(self, db_adapter, messaging_adapter):
        self.db_adapter = db_adapter
        self.messaging_adapter = messaging_adapter

    def schedule(self, task):
        """ All scheduling side effects need to be here """
        available_nodes = self.db_adapter.get_all_nodes()
        available_nodes = {}
        print("Available nodes: ", available_nodes)
        return available_nodes
    
    def publish_task_scheduled(self, job, node):
        print(f"I am using {self.messaging_adapter}")
        print("Publishing task scheduled")

    def rollback_job(self, job, node):
        print(f"I am using {self.messaging_adapter}")
        print("Rolling back job")