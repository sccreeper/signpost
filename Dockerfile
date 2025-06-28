FROM alpine:latest
RUN apk add --no-cache python3 py3-gunicorn poetry python3-dev build-base

WORKDIR /usr/signpost

COPY ./poetry.lock ./pyproject.toml /usr/signpost/

RUN poetry install

COPY . /usr/signpost/

ENV PYTHONUNBUFFERED=1

# Set default command
CMD ["sh", "./run.sh"]