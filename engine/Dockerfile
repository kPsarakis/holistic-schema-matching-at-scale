FROM maven:3-openjdk-8-slim
COPY --from=python:3.8-slim / /

LABEL maintainer="kpsarakis94@gmail.com"

WORKDIR /home/schema-matching-system/engine

COPY ./requirements.txt .
COPY ./algorithms/coma/valentine.patch .

ENV PYTHONPATH /home/schema-matching-system

RUN apt-get -qq update \
    && apt-get -qq -y install --no-install-recommends g++ gcc subversion patch dos2unix \
    && pip install -r requirements.txt \
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

# seconds that a request takes to complete
ENV SERVER_TIMEOUT 6000
# making number of threads/workers greater than number of cores improves
# the performance for a network intensive and I/O intensive application.
# threads gunicorn thread can handle a request
ENV SERVER_THREADS 2
#workers
ENV SERVER_WORKERS 1

EXPOSE 5000
# -t is the timeout in seconds. It needs to be large because some schema matching jobs might take a while
ENTRYPOINT gunicorn -b 0.0.0.0:5000 api:app -t $SERVER_TIMEOUT -w $SERVER_WORKERS --threads $SERVER_THREADS