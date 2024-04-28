from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from config.config_alembic import DATA_DB_URI

engine = create_engine(
    DATA_DB_URI,
    client_encoding="utf8",
    pool_size=50,
    # Ping the DB before sending the query (cf https://stackoverflow.com/a/66515677)
    pool_pre_ping=True,
    max_overflow=2,
    pool_recycle=300,
    pool_use_lifo=True,
    connect_args={
        "connect_timeout": 3600,
        "keepalives": 10,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 10,
    },
)
create_session = sessionmaker(bind=engine, autocommit=False)


def class_session_handler(method):
    @wraps(method)
    def _impl(self, *method_args, **method_kwargs):
        if self.session:
            return method(self, *method_args, **method_kwargs)
        try:
            self.session = create_session()
            result = method(self, *method_args, **method_kwargs)
        except Exception:
            self.session.rollback()
            raise
        finally:
            self.session.commit()
            self.session.close()
            self.session = None
        return result

    return _impl
