#!/bin/bash

# GCP Cloud Run Deployment Script
# Reads configuration from .env file

set -e  # Exit on error

echo "========================================="
echo "Deploying to Google Cloud Run"
echo "========================================="
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "ERROR: .env file not found!"
    echo "Please create .env file from .env.example"
    echo "  cp .env.example .env"
    echo "Then edit .env with your credentials."
    exit 1
fi

# Load environment variables from .env file
echo "Loading configuration from .env..."
export $(grep -v '^#' .env | grep -v '^$' | xargs)

# Set deployment configuration
SERVICE_NAME="travel-assistant-v2"
REGION="us-central1"
IMAGE_NAME="gcr.io/${GOOGLE_CLOUD_PROJECT}/${SERVICE_NAME}"

# Validate required variables
if [ -z "$GOOGLE_CLOUD_PROJECT" ]; then
    echo "ERROR: GOOGLE_CLOUD_PROJECT not set in .env"
    exit 1
fi

if [ -z "$GOOGLE_API_KEY" ]; then
    echo "ERROR: GOOGLE_API_KEY not set in .env"
    exit 1
fi

echo ""
echo "Configuration:"
echo "  Project: ${GOOGLE_CLOUD_PROJECT}"
echo "  Service: ${SERVICE_NAME}"
echo "  Region: ${REGION}"
echo ""

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo "ERROR: gcloud CLI not found. Please install it first."
    echo "Visit: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Set project
echo "Setting project to: ${GOOGLE_CLOUD_PROJECT}"
gcloud config set project ${GOOGLE_CLOUD_PROJECT}

# Build container
echo ""
echo "Building container image..."
gcloud builds submit --tag ${IMAGE_NAME}

# Prepare environment variables for Cloud Run
ENV_VARS="GOOGLE_CLOUD_PROJECT=${GOOGLE_CLOUD_PROJECT}"
ENV_VARS="${ENV_VARS},GOOGLE_API_KEY=${GOOGLE_API_KEY}"
ENV_VARS="${ENV_VARS},GEMINI_MODEL=${GEMINI_MODEL:-gemini-2.5-flash}"
ENV_VARS="${ENV_VARS},EMBEDDING_MODEL=${EMBEDDING_MODEL:-text-embedding-004}"

# Add optional Elasticsearch variables if set
if [ ! -z "$ELASTICSEARCH_URL" ]; then
    ENV_VARS="${ENV_VARS},ELASTICSEARCH_URL=${ELASTICSEARCH_URL}"
fi

if [ ! -z "$ELASTICSEARCH_API_KEY" ]; then
    ENV_VARS="${ENV_VARS},ELASTICSEARCH_API_KEY=${ELASTICSEARCH_API_KEY}"
fi

# Deploy to Cloud Run
echo ""
echo "Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
    --image ${IMAGE_NAME} \
    --platform managed \
    --region ${REGION} \
    --allow-unauthenticated \
    --set-env-vars "${ENV_VARS}" \
    --memory 2Gi \
    --cpu 2 \
    --timeout 300 \
    --max-instances 10

echo ""
echo "========================================="
echo "Deployment successful!"
echo "========================================="
echo ""
echo "Your application is now running on Cloud Run."
echo ""
echo "Get the URL with:"
echo "  gcloud run services describe ${SERVICE_NAME} --region ${REGION} --format 'value(status.url)'"
echo ""
