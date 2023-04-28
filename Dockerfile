FROM python:3.10.10-alpine3.17 as builder


ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /src

RUN apk add --no-cache gcc

RUN pip install -U pip==23.0.1 \
    && pip install poetry==1.4.2

ADD pyproject.toml poetry.lock /src/
RUN poetry export \
        --format requirements.txt \
        --output requirements.txt \
        --without-hashes \
        --with-credentials \
        && apk add --no-cache postgresql-dev \
        && mkdir /wheels \
        && pip wheel -r requirements.txt --wheel-dir /wheels \
        && rm requirements.txt

FROM python:3.10.10-alpine3.17

ENV PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_INDEX=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    LANG=C.UTF-8 \
    LC_ALL=C.UTF-8

WORKDIR /src

COPY --from=builder /wheels /wheels

RUN apk add --no-cache libpq libssl1.1 \
 && pip install /wheels/*

COPY . .

ENTRYPOINT [ "/src/bin/run.sh" ]