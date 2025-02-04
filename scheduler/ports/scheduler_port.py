from abc import ABC, abstractmethod

class SchedulerPort(ABC):
    """ Defining the Scheduler contracts """

    @abstractmethod
    def schedule(self):
        """ Schedule a job """
        pass
    @abstractmethod

    @abstractmethod
    def publish_task_scheduled(self, job, node):
        """ Publish a task scheduled event """
        pass

    @abstractmethod
    def rollback_job(self, job, node):
        """ Rollback a job in case of faliure"""
        pass