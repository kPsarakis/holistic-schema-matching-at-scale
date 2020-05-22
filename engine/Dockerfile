FROM maven:3-openjdk-8-slim
COPY --from=python:3.8-slim / /

LABEL maintainer="kpsarakis94@gmail.com"

WORKDIR /home/schema-matching-system/engine

COPY ./requirements.txt .
COPY ./algorithms/coma/valentine.patch .

ENV PYTHONPATH /home/schema-matching-system

RUN apt-get -qq update \
    && apt-get -qq -y install --no-install-recommends g++ gcc subversion patch dos2unix \
    && pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && python -m nltk.downloader stopwords \
    && python -m nltk.downloader punkt \
    && python -m nltk.downloader wordnet \
    && mkdir -p algorithms/coma \
    && cd algorithms/coma \
    && svn checkout http://svn.code.sf.net/p/coma-ce/mysvn/coma-project \
    && find . -type f -exec dos2unix {} \; \
    && patch -ruN -p1 -d  coma-project < ../../valentine.patch \
    && rm ../../valentine.patch \
    && cd coma-project \
    && mvn clean \
    && mvn -Dmaven.test.skip=true package \
    && cd .. \
    && mkdir artifact \
    && mkdir coma_output \
    && mv coma-project/coma-engine/target/coma-engine-0.1-CE-SNAPSHOT-jar-with-dependencies.jar artifact/coma.jar \
    && rm -rf coma-project \
    && apt-get -qq -y remove maven subversion patch dos2unix \
    && apt-get -qq -y autoremove \
    && apt-get autoclean

COPY . .

EXPOSE 5000