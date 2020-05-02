FROM ubuntu:18.04
LABEL maintainer="kpsarakis94@gmail.com"

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    openjdk-8-jdk gcc g++ make parallel maven subversion patch docker.io dos2unix wget

# Set environment variables
ENV JAVA_VER 8
ENV JAVA_HOME /usr/lib/jvm/java-1.8.0-openjdk-amd64

RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -u -b -p /miniconda && \
    eval "$(/miniconda/bin/conda shell.bash hook)" && \
    conda init && \
    "/miniconda/bin/conda" create -n sms38 python=3.8 -y --force

# Create project directory
RUN mkdir /home/schema-matching-system
WORKDIR /home/schema-matching-system

# Copy data to directory
COPY . .

RUN conda activate sms38 && \
    pip install -r requirements.txt && \
    python -m nltk.downloader stopwords && \
    python -m nltk.downloader punkt  && \
    python -m nltk.downloader wordnet && \
    cd algorithms/coma && \
    ./build_coma.sh

#Expose port 5000 (Flask default)
EXPOSE 5000
# -t is the timeout in seconds. It needs to be large because some schema matching jobs might take a while
CMD ["gunicorn", "-b", "0.0.0.0:5000", "api:app", "-t", "6000"]

# Run example
# docker run -p 5003:5000 schema-matching-service:latest