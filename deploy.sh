#!/bin/bash

# GCP Cloud Run Deployment Script

# Configuration
PROJECT_ID="your-project-id"
SERVICE_NAME="travel-assistant"
REGION="us-central1"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "========================================="
echo "Deploying to Google Cloud Run"
echo "========================================="
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not found. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "Setting project to: ${PROJECT_ID}"
gcloud config set project ${PROJECT_ID}

# Build container
echo ""
echo "Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

if [ $? -ne 0 ]; then
    echo "ERROR: Build failed"
    exit 1
fi

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
    --set-env-vars "ELASTICSEARCH_URL=https://my-elasticsearch-project-f06d88.es.us-central1.gcp.elastic.cloud:443" \
    --set-env-vars "ELASTICSEARCH_API_KEY=ZUNOc3U1a0JRMmJEeDN5RFhMSFE6VlNHdHlwQU9OZldvMDktRGRvdU5LQQ==" \
    --set-env-vars "GEMINI_MODEL=gemini-1.5-flash" \
    --set-env-vars "EMBEDDING_MODEL=text-embedding-004" \
    --memory 1Gi \
    --timeout 300

if [ $? -eq 0 ]; then
    echo ""
    echo "========================================="
    echo "Deployment successful!"
    echo "========================================="
    echo ""
    echo "Your application is now running on Cloud Run."
    echo "Get the URL with:"
    echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'"
else
    echo "ERROR: Deployment failed"
    exit 1
fi
