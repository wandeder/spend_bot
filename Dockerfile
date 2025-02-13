FROM python:3.10-slim
LABEL authors="Dmirtii Morozov"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock /app/

RUN poetry install --no-root

COPY ./spend_bot /app/spend_bot

CMD ["poetry", "run", "python", "./spend_bot/bot.py"]
