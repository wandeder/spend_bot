FROM python:3.10-slim
LABEL authors="Dmirtii Morozov"

# set working directory
WORKDIR /app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN pip install poetry

COPY ./pyproject.toml ./poetry.lock* /app/

RUN poetry export -f requirements.txt --output requirements.txt --without-hashes

# install python dependencies
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

# add app
COPY ./spend_bot /app/spend_bot

ENTRYPOINT ["python3", "-m", "spend_bot.bot"]
