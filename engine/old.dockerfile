FROM maven:3-openjdk-8-slim
COPY --from=python:3.8-slim / /

LABEL maintainer="kpsarakis94@gmail.com"

WORKDIR /home/schema-matching-system/engine

COPY ./requirements.txt .
COPY ./algorithms/coma/valentine.patch .

ENV PYTHONPATH /home/schema-matching-system

RUN apt-get -qq update \
    && apt-get -qq -y install --no-install-recommends g++ gcc git patch dos2unix \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m nltk.downloader stopwords \
    && python -m nltk.downloader punkt \
    && python -m nltk.downloader wordnet \
    && mkdir -p algorithms/coma \
    && cd algorithms/coma \
    && git clone https://github.com/kPsarakis/COMA \
    && find . -type f -exec dos2unix {} \; \
    && patch -ruN -p1 -d  COMA < ../../valentine.patch \
    && rm ../../valentine.patch \
    && cd COMA \
    && mvn clean \
    && mvn -Dmaven.test.skip=true package \
    && cd .. \
    && mkdir artifact \
    && mkdir coma_output \
    && mv COMA/coma-engine/target/coma-engine-0.1-CE-SNAPSHOT-jar-with-dependencies.jar artifact/coma.jar \
    && rm -rf COMA \
    && apt-get -qq -y remove maven git patch dos2unix \
    && apt-get -qq -y autoremove \
    && apt-get autoclean

COPY . .

EXPOSE 5000

CMD gunicorn -b 0.0.0.0:5000 app:app