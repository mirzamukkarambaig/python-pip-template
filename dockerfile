FROM python:3.10-alpine


ARG ENVIORNMENT=dev
ENV ENVIORNMENT=${ENVIORNMENT}

COPY src /app/src
COPY pyproject.toml /app/
COPY tests /app/tests

WORKDIR /app

RUN apk add --no-cache gcc musl-dev libffi-dev

RUN pip install --upgrade pip


RUN pip install -e ".[${ENVIORNMENT}]"

CMD [ "app" ]
