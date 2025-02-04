from scheduler.ports.scheduler_port import SchedulerPort
from database.ports.database_ports import DatabasePort
from common.ports.messaging_ports import MessagingPort
from database.controllers.worker import Worker
import oslo_messaging

import random 
class FederatedScheduler(SchedulerPort):
    def __init__(self, db_adapter: DatabasePort, messaging_adapter: MessagingPort):
        self.db_adapter = db_adapter
        self.messaging_adapter = messaging_adapter

    def schedule(self, context, job_data):
        """Selects a node and forwards the job to the corresponding worker queue."""
        nodes = Worker(self.db_adapter.get_session(), context)
        available_nodes = nodes.list_all(context)
        available_nodes_hostnames = [hostname for hostname in available_nodes['hostname']]
        selected_node = random.choice(available_nodes_hostnames)
        """ Now that we have the right node we need a client for that node """
        client = self.messaging_adapter.get_client(selected_node)
        job_data["assigned_node"] = selected_node
        """ Now we can send the job to the node """
        self.messaging_adapter.cast_async(context, job_data)

        print(f"Scheduled job {job_data['job_id']} to {selected_node}")
        """ Here we actually should return the task/job spec so we can do things with it, ie, publish or roll back """
        return available_nodes
    
    def publish_task_scheduled(self, context, job, node):
        print(f"I am using {self.messaging_adapter}")
        print("Publishing task scheduled")

    def rollback_job(self, context, job, node):
        print(f"I am using {self.messaging_adapter}")
        print("Rolling back job")