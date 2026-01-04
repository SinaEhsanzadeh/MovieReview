FROM python:3.12-slim 

ENV PYTHONUNBUFFERED=1 PYTHONDONTWRITEBYTECODE=1 

WORKDIR /app

RUN pip install poetry

RUN poetry config virtualenvs.create false 

COPY pyproject.toml poetry.lock* /app/

RUN poetry install --no-interaction --no-ansi --no-root

COPY app/ ./app/
COPY alembic/ ./alembic
COPY alembic.ini ./ 

CMD ["bash", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"]
