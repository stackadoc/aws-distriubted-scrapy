FROM python:3.10.12-slim

ENV YOUR_ENV=PYTHONFAULTHANDLER=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONHASHSEED=random \
  PYTHONDONTWRITEBYTECODE=1 \
  PIP_DISABLE_PIP_VERSION_CHECK=on \
  PIP_NO_CACHE_DIR=off \
  PIP_DEFAULT_TIMEOUT=100 \
  POETRY_VERSION=1.3.1

RUN pip install "poetry==$POETRY_VERSION"

WORKDIR /code

COPY poetry.lock pyproject.toml /code/
RUN poetry install --no-interaction --no-ansi


COPY scraper/ /code/scraper/
COPY scrapyd.conf /code/scrapyd.conf
COPY scrapyd.sh /code/scrapyd.sh

ENTRYPOINT ["/bin/sh", "/code/scrapyd.sh"]