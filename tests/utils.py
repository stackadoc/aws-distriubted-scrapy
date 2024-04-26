import datetime
import json
from typing import List
from unittest import TestCase

import freezegun
import psycopg2
from freezegun import freeze_time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from libs.database.db_data.db_data_models import Base


DATABASE = {
    "ENGINE": "postgresql",
    "NAME": "test_database",
    "USER": "postgres",
    "PASSWORD": "postgres",
    "HOST": "localhost",
    "PORT": "5432",
}

def mock_fetch_airtable_all_multithreaded(table_name, *args, **kwargs):
    with open(f"tests/test_data/airtable/{table_name}_table.json", "r") as file:
        return json.load(file)

def create_test_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DATABASE["USER"],
        password=DATABASE["PASSWORD"],
        host=DATABASE["HOST"],
        port=DATABASE["PORT"],
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"CREATE DATABASE {DATABASE['NAME']}")
    cur.close()
    conn.close()

def delete_test_database():
    conn = psycopg2.connect(
        dbname="postgres",
        user=DATABASE["USER"],
        password=DATABASE["PASSWORD"],
        host=DATABASE["HOST"],
        port=DATABASE["PORT"],
    )
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute(f"DROP DATABASE IF EXISTS {DATABASE['NAME']} WITH (FORCE)")
    cur.close()
    conn.close()


class TestCaseDB(TestCase):
    @classmethod
    def setUpClass(cls):
        create_test_database()
        cls.REF_DB_URI = (
            f"postgresql://{DATABASE['USER']}:{DATABASE['PASSWORD']}"
            + f"@{DATABASE['HOST']}:{DATABASE['PORT']}/{DATABASE['NAME']}"
        )
        cls.engine = create_engine(cls.REF_DB_URI, client_encoding="utf8", pool_size=50)
        Base.metadata.create_all(cls.engine)
        cls._create_session = sessionmaker(bind=cls.engine)

    def setUp(self):
        self.session = self._create_session()

    def tearDown(self):
        self.session.rollback()
        self.session.close()

    @classmethod
    def tearDownClass(cls):
        delete_test_database()