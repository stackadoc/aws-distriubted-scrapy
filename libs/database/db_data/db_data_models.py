import datetime
from dataclasses import dataclass, field

from sqlalchemy import Column, DateTime, Float, Integer, LargeBinary, String
from sqlalchemy.orm import registry

mapper_registry = registry()
Base = mapper_registry.generate_base()


@mapper_registry.mapped
@dataclass
class SpiderJob:
    __sa_dataclass_metadata_key__ = "sa"
    __tablename__ = "spider_job"

    id: int = field(init=False, metadata={"sa": Column(Integer, primary_key=True)})

    priority: float = field(default=None, metadata={"sa": Column(Float)})
    message: bytes = field(default=None, metadata={"sa": Column(LargeBinary)})

    status: str = field(default=None, metadata={"sa": Column(String)})

    project: str = field(default=None, metadata={"sa": Column(String)})
    spider: str = field(default=None, metadata={"sa": Column(String)})
    job: str = field(default=None, metadata={"sa": Column(String)})
    start_time: datetime.datetime = field(default=None, metadata={"sa": Column(DateTime)})
    end_time: datetime.datetime = field(default=None, metadata={"sa": Column(DateTime)})
