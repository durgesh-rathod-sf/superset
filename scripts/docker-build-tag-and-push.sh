#!/bin/bash

set -e

# optional
: "${AWS_REGION:=us-east-1}"
: "${ENVIRONMENT:=poc}"

## required
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query "Account" --output text)
: "${IMAGE_TAG:-$IMAGE_TAG}"

ECR_REGISTRY_ENDPOINT="$AWS_ACCOUNT_ID.dkr.ecr.$AWS_REGION.amazonaws.com"
IMAGE_NAME="$ECR_REGISTRY_ENDPOINT/superset-base"

echo "Account: $AWS_ACCOUNT_ID"

printf "\nECR Login...\n"
aws ecr get-login-password \
  --region $AWS_REGION \
  | docker login \
      --username AWS \
      --password-stdin $ECR_REGISTRY_ENDPOINT

printf "\nBuilding docker images...\n"
docker build -t sourcefuse/superset-base:latest .

printf "\nTagging image $IMAGE_NAME:$IMAGE_TAG...\n"
docker tag sourcefuse/superset-base:latest $IMAGE_NAME:$IMAGE_TAG

printf "\nPushing $IMAGE_NAME:$IMAGE_TAG to ECR...\n"
docker push $IMAGE_NAME:$IMAGE_TAG

echo "::set-output name=image::$IMAGE_NAME:$IMAGE_TAG"
