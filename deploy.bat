@echo off
REM GCP Cloud Run Deployment Script for Windows

REM Configuration - UPDATE THESE VALUES
set PROJECT_ID=ai-accelerate-devpost
set GEMINI_API_KEY=AIzaSyBCSkT3M4TNZxwiwzC8ieSgTQ3u4Hbm5q0
set SERVICE_NAME=travel-assistant-v2
set REGION=us-central1
set IMAGE_NAME=gcr.io/%PROJECT_ID%/%SERVICE_NAME%

echo =========================================
echo Deploying to Google Cloud Run
echo =========================================
echo.

REM Check if gcloud is installed
where gcloud >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: gcloud CLI not found. Please install it first.
    echo Visit: https://cloud.google.com/sdk/docs/install
    pause
    exit /b 1
)

REM Set project
echo Setting project to: %PROJECT_ID%
gcloud config set project %PROJECT_ID%

REM Build container
echo.
echo Building container image...
gcloud builds submit --tag %IMAGE_NAME%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Deploy to Cloud Run
echo.
echo Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME% ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --set-env-vars "GOOGLE_CLOUD_PROJECT=%PROJECT_ID%" ^
    --set-env-vars "GOOGLE_API_KEY=%GEMINI_API_KEY%" ^
    --set-env-vars "ELASTICSEARCH_URL=https://my-elasticsearch-project-f06d88.es.us-central1.gcp.elastic.cloud:443" ^
    --set-env-vars "ELASTICSEARCH_API_KEY=ZUNOc3U1a0JRMmJEeDN5RFhMSFE6VlNHdHlwQU9OZldvMDktRGRvdU5LQQ==" ^
    --set-env-vars "GEMINI_MODEL=gemini-2.5-flash" ^
    --set-env-vars "EMBEDDING_MODEL=text-embedding-004" ^
    --memory 2Gi ^
    --cpu 2 ^
    --timeout 300 ^
    --max-instances 10

if %ERRORLEVEL% EQU 0 (
    echo.
    echo =========================================
    echo Deployment successful!
    echo =========================================
    echo.
    echo Your application is now running on Cloud Run.
    echo Get the URL with:
    echo   gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"
) else (
    echo ERROR: Deployment failed
    pause
    exit /b 1
)

pause
