# Build  COMA and its dependancies from source
FROM maven:3-openjdk-8-slim as build-stage-COMA

RUN apt-get update && apt-get -y install git patch dos2unix

WORKDIR /usr/local

COPY ./algorithms/coma/valentine.patch /usr/local

RUN git clone https://github.com/kPsarakis/COMA \
    && find . -type f -exec dos2unix {} \; \
    && patch -ruN -p1 -d  COMA < /usr/local/valentine.patch \
    && cd COMA \
    && mvn clean \
    && mvn -Dmaven.test.skip=true package \
    && mv coma-engine/target/coma-engine-0.1-CE-SNAPSHOT-jar-with-dependencies.jar /usr/local/coma.jar

# Build the algorithms module
FROM python:3.8-slim as build-stage-algorithms

RUN apt-get update && apt-get install -y gcc g++

COPY requirements-algorithms.txt /var/local/algorithms/

RUN pip3 install --upgrade pip \
    && pip3 install --prefix=/usr/local -r /var/local/algorithms/requirements-algorithms.txt \
    && python -m nltk.downloader -d /usr/local/share/nltk_data stopwords punkt wordnet

# Create the final service
FROM openjdk:8-slim
COPY --from=python:3.8-slim / /

RUN groupadd flask \
    && useradd -m -d /var/local/schema-matching-system -g flask flask

COPY --from=build-stage-algorithms /usr/local/ /usr/local

WORKDIR /usr/local/schema-matching-system/engine

COPY requirements-server.txt .

RUN pip3 install --no-cache-dir --upgrade pip \
    && pip3 install --no-cache-dir --prefix=/usr/local -r requirements-server.txt

COPY . .

COPY --from=build-stage-COMA /usr/local/coma.jar algorithms/coma/artifact

ENV PYTHONPATH /usr/local/schema-matching-system

USER flask

EXPOSE 5000

CMD gunicorn -b 0.0.0.0:5000 app:app
