FROM ubuntu:20.04
LABEL maintainer="kpsarakis94@gmail.com"

WORKDIR /home/schema-matching-system/engine

COPY . .

ENV JAVA_VERSION 8
ENV PYTHON_VERSION 3.8
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64
ENV PATH /opt/conda/bin:$PATH
ENV PYTHONPATH /home/schema-matching-system

RUN apt-get -qq update \
    && apt-get -qq -y install --no-install-recommends curl bzip2 gcc g++ openjdk-8-jdk maven subversion patch dos2unix \
    && curl -sSL https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o /tmp/miniconda.sh \
    && bash /tmp/miniconda.sh -bfp /usr/local \
    && rm -rf /tmp/miniconda.sh \
    && conda install -y python="$PYTHON_VERSION" \
    && conda update conda \
    && pip install -r requirements.txt \
    && python -m nltk.downloader stopwords \
    && python -m nltk.downloader punkt \
    && python -m nltk.downloader wordnet \
    && cd algorithms/coma \
    && svn checkout http://svn.code.sf.net/p/coma-ce/mysvn/coma-project \
    && find . -type f -exec dos2unix {} \; \
    && patch -ruN -p1 -d  coma-project < valentine.patch \
    && cd coma-project \
    && mvn clean \
    && mvn -Dmaven.test.skip=true package \
    && cd .. \
    && mkdir artifact \
    && mkdir coma_output \
    && mv coma-project/coma-engine/target/coma-engine-0.1-CE-SNAPSHOT-jar-with-dependencies.jar artifact/coma.jar \
    && rm -rf coma-project \
    && apt-get -qq -y remove curl bzip2 maven subversion patch dos2unix \
    && apt-get -qq -y autoremove \
    && apt-get autoclean \
    && rm -rf /var/lib/apt/lists/* /var/log/dpkg.log \
    && conda clean --all --yes

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
CMD gunicorn -b 0.0.0.0:5000 api:app -t $SERVER_TIMEOUT -w $SERVER_WORKERS --threads $SERVER_THREADS