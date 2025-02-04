from abc import ABC, abstractmethod

class SchedulerPort(ABC):
    """ Defining the Scheduler contracts """

    @abstractmethod
    def schedule(self, context, job_data):
        """ Schedule a job """
        pass
    
    @abstractmethod
    def publish_task_scheduled(self, context, job, node):
        """ Publish a task scheduled event """
        pass

    @abstractmethod
    def rollback_job(self,context, job, node):
        """ Rollback a job in case of faliure"""
        pass