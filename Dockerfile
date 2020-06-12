FROM python:3.5

WORKDIR /usr/src/app

ENV APP_NAME respa

RUN apt-get update && apt-get install -y libgdal20 postgresql-client rabbitmq-server

# We downgrade pip, since versions 10+ break dependency resolution in pip-compile
RUN python -m pip install pip==9.0.3

COPY requirements.txt .
COPY deploy/requirements.txt ./deploy/requirements.txt

RUN pip install --no-cache-dir -r deploy/requirements.txt

COPY . .

RUN pip-compile --output-file requirements_local.txt requirements_local.in
RUN pip install -r requirements_local.txt

# Create Exchange sync folders
RUN mkdir /exchange_sync
RUN mkdir /exchange_sync/logs

CMD service rabbitmq-server start && deploy/server.sh
