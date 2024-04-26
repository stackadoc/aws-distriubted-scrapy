from scrapyd.interfaces import IJobStorage
from scrapyd.jobstorage import Job
from zope.interface import implementer

from libs.scrapy_queue.postgres import PostgresFinishedJobs


@implementer(IJobStorage)
class PostgresJobStorage(object):
    def __init__(self, config, session=None):
        self.jstorage = PostgresFinishedJobs(session=session)
        self.finished_to_keep = config.getint("finished_to_keep", 100)

    def add(self, job):
        self.jstorage.add(job)
        self.jstorage.clear(self.finished_to_keep)

    def list(self):
        return list(self.__iter__())

    def __len__(self):
        return len(self.jstorage)

    def __iter__(self):
        for j in self.jstorage:
            yield Job(project=j[0], spider=j[1], job=j[2], start_time=j[3], end_time=j[4])
