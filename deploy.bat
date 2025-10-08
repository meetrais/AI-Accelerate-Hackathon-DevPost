@echo off
REM GCP Cloud Run Deployment Script for Windows
REM Reads configuration from .env file

echo =========================================
echo Deploying to Google Cloud Run
echo =========================================
echo.

REM Check if .env file exists
if not exist .env (
    echo ERROR: .env file not found!
    echo Please create .env file from .env.example
    echo   copy .env.example .env
    echo Then edit .env with your credentials.
    pause
    exit /b 1
)

REM Load environment variables from .env file
echo Loading configuration from .env...
for /f "usebackq tokens=1,* delims==" %%a in (.env) do (
    set "line=%%a"
    REM Skip comments and empty lines
    if not "!line:~0,1!"=="#" if not "%%a"=="" (
        set "%%a=%%b"
    )
)

REM Set deployment configuration
set SERVICE_NAME=travel-assistant-v2
set REGION=us-central1
set IMAGE_NAME=gcr.io/%GOOGLE_CLOUD_PROJECT%/%SERVICE_NAME%

REM Validate required variables
if "%GOOGLE_CLOUD_PROJECT%"=="" (
    echo ERROR: GOOGLE_CLOUD_PROJECT not set in .env
    pause
    exit /b 1
)
if "%GOOGLE_API_KEY%"=="" (
    echo ERROR: GOOGLE_API_KEY not set in .env
    pause
    exit /b 1
)

echo.
echo Configuration:
echo   Project: %GOOGLE_CLOUD_PROJECT%
echo   Service: %SERVICE_NAME%
echo   Region: %REGION%
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
echo Setting project to: %GOOGLE_CLOUD_PROJECT%
gcloud config set project %GOOGLE_CLOUD_PROJECT%

REM Build container
echo.
echo Building container image...
gcloud builds submit --tag %IMAGE_NAME%

if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Build failed
    pause
    exit /b 1
)

REM Prepare environment variables for Cloud Run
set ENV_VARS=GOOGLE_CLOUD_PROJECT=%GOOGLE_CLOUD_PROJECT%
set ENV_VARS=%ENV_VARS%,GOOGLE_API_KEY=%GOOGLE_API_KEY%
set ENV_VARS=%ENV_VARS%,GEMINI_MODEL=%GEMINI_MODEL%
set ENV_VARS=%ENV_VARS%,EMBEDDING_MODEL=%EMBEDDING_MODEL%

REM Add optional Elasticsearch variables if set
if not "%ELASTICSEARCH_URL%"=="" (
    set ENV_VARS=%ENV_VARS%,ELASTICSEARCH_URL=%ELASTICSEARCH_URL%
)
if not "%ELASTICSEARCH_API_KEY%"=="" (
    set ENV_VARS=%ENV_VARS%,ELASTICSEARCH_API_KEY=%ELASTICSEARCH_API_KEY%
)

REM Deploy to Cloud Run
echo.
echo Deploying to Cloud Run...
gcloud run deploy %SERVICE_NAME% ^
    --image %IMAGE_NAME% ^
    --platform managed ^
    --region %REGION% ^
    --allow-unauthenticated ^
    --set-env-vars "%ENV_VARS%" ^
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
    echo.
    echo Get the URL with:
    echo   gcloud run services describe %SERVICE_NAME% --region %REGION% --format "value(status.url)"
    echo.
) else (
    echo ERROR: Deployment failed
    pause
    exit /b 1
)

pause
