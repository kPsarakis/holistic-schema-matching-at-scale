# Build  COMA and its dependancies from source
FROM maven:3-openjdk-8-slim as build-stage-COMA

RUN apt-get update && apt-get -y --no-install-recommends install git=1:2.20.1* patch=2.7.6* dos2unix=7.4.0*

WORKDIR /usr/local

COPY ./algorithms/coma/valentine.patch /usr/local

RUN git clone https://github.com/kPsarakis/COMA \
    && find . -type f -exec dos2unix {} \; \
    && patch -ruN -p1 -d  COMA < /usr/local/valentine.patch \
    && mvn -f COMA/pom.xml clean \
    && mvn -f COMA/pom.xml -Dmaven.test.skip=true package \
    && mv COMA/coma-engine/target/coma-engine-0.1-CE-SNAPSHOT-jar-with-dependencies.jar /usr/local/coma.jar

# Python dependancies builder
FROM python:3.8-slim as builder

RUN apt-get update && apt-get install -y --no-install-recommends gcc=4:8.3* g++=4:8.3*

COPY requirements.txt /var/local/schema-matching-system/

RUN pip3 install --upgrade pip==20.3.1 \
    && pip3 install --prefix=/usr/local -r /var/local/schema-matching-system/requirements.txt \
    && python -m nltk.downloader -d /usr/local/share/nltk_data stopwords punkt wordnet

# Clean Python 3.8 env
FROM python:3.8-slim as clean-Python

# Create the final service
FROM openjdk:8-slim
COPY --from=clean-Python / /

COPY --from=builder /usr/local/ /usr/local

RUN mkdir /usr/local/schema-matching-system \
    && groupadd flask \
    && useradd -m -d /usr/local/schema-matching-system/engine -g flask flask

WORKDIR /usr/local/schema-matching-system/engine

COPY --chown=flask . .

COPY --chown=flask --from=build-stage-COMA /usr/local/coma.jar algorithms/coma/artifact

ENV PYTHONPATH /usr/local/schema-matching-system

EXPOSE 5000

USER flask

CMD gunicorn -b 0.0.0.0:5000 app:app
