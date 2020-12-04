#!/usr/bin/env bash

helm repo add minio https://helm.min.io/
# helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm install --set accessKey=minio,secretKey=minio123,persistence.size=4Gi,mode=distributed,replicas=4,resources.requests.memory=4Gi minio stable/minio
helm install my-release ingress-nginx/ingress-nginx