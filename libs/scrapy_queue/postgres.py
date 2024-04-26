import json
from datetime import datetime

from config import config
from libs.database.db_data.db_data_helper import class_session_handler
from libs.database.db_data.db_data_models import SpiderJob


class PostgresPriorityQueue(object):
    def __init__(self, session=None):
        self.session = session
        self._table_name = SpiderJob.__tablename__
        self.execution_ref = config.DB_EXECUTION_NAME

    @class_session_handler
    def put(self, message, priority=0.0):
        record = SpiderJob(
            spider=message.get("name"),
            job=message.get("_job"),
            execution_ref=self.execution_ref,
            priority=priority,
            status="pending",
            message=self.encode(message),
        )
        self.session.add(record)

    @class_session_handler
    def pop(self):
        self.session.execute(f"LOCK TABLE {self._table_name} IN SHARE ROW EXCLUSIVE MODE")
        record = (
            self.session.query(SpiderJob)
            .filter(SpiderJob.status == "pending", SpiderJob.execution_ref == self.execution_ref)
            .order_by(SpiderJob.priority.desc())
            .first()
        )
        if not record:
            return None
        record.status = "ongoing"
        self.session.add(record)
        return self.decode(record.message)

    @class_session_handler
    def remove(self, func):
        records = (
            self.session.query(SpiderJob)
            .filter(SpiderJob.status == "pending", SpiderJob.execution_ref == self.execution_ref)
            .all()
        )
        n = 0
        for record in records:
            if func(self.decode(record.message)):
                self.session.delete(record)
                n += 1
        return n

    @class_session_handler
    def clear(self):
        self.session.query(SpiderJob).filter(
            SpiderJob.status == "pending", SpiderJob.execution_ref == self.execution_ref
        ).delete()

    @class_session_handler
    def __len__(self):
        return (
            self.session.query(SpiderJob)
            .filter(SpiderJob.status == "pending", SpiderJob.execution_ref == self.execution_ref)
            .count()
        )

    @class_session_handler
    def __iter__(self):
        records = (
            self.session.query(SpiderJob)
            .filter(SpiderJob.status == "pending", SpiderJob.execution_ref == self.execution_ref)
            .order_by(SpiderJob.priority.desc())
            .all()
        )
        return ((self.decode(record.message), record.priority) for record in records)

    @class_session_handler
    def encode(self, obj):
        return json.dumps(obj).encode("ascii")

    @class_session_handler
    def decode(self, text):
        return json.loads(bytes(text).decode("ascii"))


class PostgresFinishedJobs(object):
    def __init__(self, session=None):
        self.session = session
        self.execution_ref = config.DB_EXECUTION_NAME

    @class_session_handler
    def add(self, job):
        record = (
            self.session.query(SpiderJob)
            .filter(
                SpiderJob.spider == job.spider,
                SpiderJob.job == job.job,
                SpiderJob.execution_ref == self.execution_ref,
            )
            .first()
        )
        if record:
            record.project = job.project
            record.start_time = job.start_time
            record.end_time = job.end_time
            record.status = "terminated"
        else:
            record = SpiderJob(
                project=job.project,
                spider=job.spider,
                job=job.job,
                start_time=job.start_time,
                end_time=job.end_time,
                status="terminated",
                execution_ref=self.execution_ref,
            )
        self.session.add(record)

    @class_session_handler
    def clear(self, finished_to_keep=None):
        if finished_to_keep:
            limit = len(self) - finished_to_keep
            if limit > 0:
                subquery = (
                    self.session.query(SpiderJob.id)
                    .filter(
                        SpiderJob.status == "terminated",
                        SpiderJob.execution_ref == self.execution_ref,
                    )
                    .order_by(SpiderJob.end_time)
                    .limit(limit)
                )
                self.session.query(SpiderJob).filter(SpiderJob.id.in_(subquery)).delete(
                    synchronize_session=False
                )
        else:
            self.session.query(SpiderJob).filter(
                SpiderJob.status == "terminated", SpiderJob.execution_ref == self.execution_ref
            ).delete()

    @class_session_handler
    def __len__(self):
        return (
            self.session.query(SpiderJob)
            .filter(SpiderJob.status == "terminated", SpiderJob.execution_ref == self.execution_ref)
            .count()
        )

    @class_session_handler
    def __iter__(self):
        records = (
            self.session.query(SpiderJob)
            .filter(SpiderJob.status == "terminated", SpiderJob.execution_ref == self.execution_ref)
            .order_by(SpiderJob.end_time.desc())
            .all()
        )
        self.session.expunge_all()
        return (
            (
                record.project,
                record.spider,
                record.job,
                datetime.strptime(str(record.start_time), "%Y-%m-%d %H:%M:%S.%f"),
                datetime.strptime(str(record.end_time), "%Y-%m-%d %H:%M:%S.%f"),
            )
            for record in records
        )
