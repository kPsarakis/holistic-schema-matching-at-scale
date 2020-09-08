#!/usr/bin/env bash

helm install --set accessKey=minio,secretKey=minio123,persistence.size=1Gi,mode=distributed,replicas=4,resources.requests.memory=1Gi minio stable/minio

cd k8s/ && \
  kubectl apply -f . && \
  cd ..