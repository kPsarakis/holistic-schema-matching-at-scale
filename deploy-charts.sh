#!/usr/bin/env bash

helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx

helm repo update

helm install -f helm-config/minio-helm-values.yaml minio bitnami/minio
helm install -f helm-config/redis-helm-values.yaml redis bitnami/redis
helm install my-release ingress-nginx/ingress-nginx