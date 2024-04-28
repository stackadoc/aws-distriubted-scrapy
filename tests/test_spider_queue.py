import os
from unittest.mock import patch

from scrapyd.config import Config
from scrapyd.interfaces import IJobStorage, ISpiderQueue
from scrapyd.jobstorage import Job
from twisted.internet.defer import inlineCallbacks, maybeDeferred
from twisted.trial import unittest
from zope.interface.verify import verifyObject

from libs.scrapy_queue import job_storage, spider_queue
from tests.utils import TestCaseDB


class SpiderQueueTest(TestCaseDB):
    """This test case also supports queues with deferred methods."""

    @patch.dict(os.environ, {"DB_EXECUTION_NAME": "DEV_TEST"}, clear=True)
    def setUp(self):
        super().setUp()
        self.q = spider_queue.PostgresSpiderQueue(
            Config(values={"dbs_dir": ":memory:"}), "quotesbot", session=self.session
        )
        self.name = "spider1"
        self.priority = 5
        self.args = {
            "arg1": "val1",
            "arg2": 2,
            "arg3": "\N{SNOWMAN}",
        }
        self.msg = self.args.copy()
        self.msg["name"] = self.name

    def test_interface(self):
        verifyObject(ISpiderQueue, self.q)

    @patch.dict(os.environ, {"DB_EXECUTION_NAME": "DEV_TEST"}, clear=True)
    @inlineCallbacks
    def test_add_pop_count(self):
        c = yield maybeDeferred(self.q.count)
        self.assertEqual(c, 0)

        yield maybeDeferred(self.q.add, self.name, self.priority, **self.args)

        c = yield maybeDeferred(self.q.count)
        self.assertEqual(c, 1)

        m = yield maybeDeferred(self.q.pop)
        self.assertEqual(m, self.msg)

        c = yield maybeDeferred(self.q.count)
        self.assertEqual(c, 0)

    @patch.dict(os.environ, {"DB_EXECUTION_NAME": "DEV_TEST"}, clear=True)
    @inlineCallbacks
    def test_list(self):
        actual = yield maybeDeferred(self.q.list)
        self.assertEqual(actual, [])

        yield maybeDeferred(self.q.add, self.name, self.priority, **self.args)
        yield maybeDeferred(self.q.add, self.name, self.priority, **self.args)

        actual = yield maybeDeferred(self.q.list)
        self.assertEqual(actual, [self.msg, self.msg])

    @patch.dict(os.environ, {"DB_EXECUTION_NAME": "DEV_TEST"}, clear=True)
    @inlineCallbacks
    def test_clear(self):
        yield maybeDeferred(self.q.add, self.name, self.priority, **self.args)
        yield maybeDeferred(self.q.add, self.name, self.priority, **self.args)

        c = yield maybeDeferred(self.q.count)
        self.assertEqual(c, 2)

        yield maybeDeferred(self.q.clear)

        c = yield maybeDeferred(self.q.count)
        self.assertEqual(c, 0)


class PostgresJobsStorageTest(TestCaseDB, unittest.TestCase):
    def setUp(self):
        super().setUp()
        d = self.mktemp()
        config = Config(values={"dbs_dir": d, "finished_to_keep": "2"})
        self.jobst = job_storage.PostgresJobStorage(config, session=self.session)
        self.j1, self.j2, self.j3 = Job("p1", "s1"), Job("p2", "s2"), Job("p3", "s3")

    def test_interface(self):
        verifyObject(IJobStorage, self.jobst)

    def test_add(self):
        self.jobst.add(self.j1)
        self.jobst.add(self.j2)
        self.jobst.add(self.j3)

        self.assertEqual(len(self.jobst.list()), 2)

    def test_iter(self):
        self.jobst.add(self.j1)
        self.jobst.add(self.j2)
        self.jobst.add(self.j3)

        self.assertEqual(len(self.jobst), 2)
