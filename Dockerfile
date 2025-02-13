FROM python:3.10-slim
LABEL authors="Dmirtii Morozov"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install

COPY ./spend_bot /app/spend_bot

ENTRYPOINT ["python3", "-m", "spend_bot.bot"]
