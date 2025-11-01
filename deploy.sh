#!/bin/bash
# Quick deployment script for Project Younicorn to GCP Cloud Run

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Project Younicorn - GCP Deployment${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if gcloud is installed
if ! command -v gcloud &> /dev/null; then
    echo -e "${RED}Error: gcloud CLI is not installed${NC}"
    echo "Install it from: https://cloud.google.com/sdk/docs/install"
    exit 1
fi

# Get project ID
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}Error: No GCP project configured${NC}"
    echo "Run: gcloud init"
    exit 1
fi

echo -e "${GREEN}✓ Using GCP Project: $PROJECT_ID${NC}\n"

# Set variables
REGION="us-central1"
BACKEND_SERVICE="younicorn-backend"
FRONTEND_SERVICE="younicorn-frontend"

# Function to deploy backend
deploy_backend() {
    echo -e "${YELLOW}Deploying Backend...${NC}"
    
    gcloud run deploy $BACKEND_SERVICE \
        --source . \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 8080 \
        --memory 4Gi \
        --cpu 2 \
        --timeout 900 \
        --max-instances 10 \
        --min-instances 0 \
        --concurrency 80 \
        --no-cpu-throttling \
        --set-env-vars="APP_ENV=production,BIGQUERY_DATASET=minerva_dataset,BIGQUERY_LOCATION=US" \
        --quiet
    
    # Get backend URL
    BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
        --region $REGION \
        --format 'value(status.url)')
    
    echo -e "${GREEN}✓ Backend deployed at: $BACKEND_URL${NC}\n"
    echo "$BACKEND_URL" > .backend_url
}

# Function to deploy frontend
deploy_frontend() {
    echo -e "${YELLOW}Deploying Frontend...${NC}"
    
    # Get backend URL
    if [ -f .backend_url ]; then
        BACKEND_URL=$(cat .backend_url)
    else
        BACKEND_URL=$(gcloud run services describe $BACKEND_SERVICE \
            --region $REGION \
            --format 'value(status.url)' 2>/dev/null || echo "")
    fi
    
    if [ -z "$BACKEND_URL" ]; then
        echo -e "${RED}Error: Backend URL not found. Deploy backend first.${NC}"
        exit 1
    fi
    
    cd frontend
    
    # Load Firebase config from .env file if it exists
    if [ -f .env ]; then
        set -a  # automatically export all variables
        source .env
        set +a
    fi
    
    # Check if Firebase variables are set
    if [ -z "$VITE_FIREBASE_API_KEY" ]; then
        echo -e "${RED}Warning: Firebase environment variables not found in .env file${NC}"
        echo -e "${YELLOW}Frontend will deploy but Firebase authentication may not work${NC}"
    else
        echo -e "${GREEN}✓ Firebase config loaded from .env${NC}"
        echo -e "${YELLOW}API Key: ${VITE_FIREBASE_API_KEY:0:20}...${NC}"
        echo -e "${YELLOW}Project ID: $VITE_FIREBASE_PROJECT_ID${NC}"
    fi
    
    # Create .env.production file for Docker build
    echo -e "${YELLOW}Creating .env.production for Docker build...${NC}"
    echo -e "${YELLOW}Backend URL: $BACKEND_URL${NC}"
    cat > .env.production << EOF
VITE_API_BASE_URL=$BACKEND_URL
VITE_LANGGRAPH_URL=$BACKEND_URL
VITE_API_URL=$BACKEND_URL
VITE_FIREBASE_API_KEY=$VITE_FIREBASE_API_KEY
VITE_FIREBASE_AUTH_DOMAIN=$VITE_FIREBASE_AUTH_DOMAIN
VITE_FIREBASE_PROJECT_ID=$VITE_FIREBASE_PROJECT_ID
VITE_FIREBASE_STORAGE_BUCKET=$VITE_FIREBASE_STORAGE_BUCKET
VITE_FIREBASE_MESSAGING_SENDER_ID=$VITE_FIREBASE_MESSAGING_SENDER_ID
VITE_FIREBASE_APP_ID=$VITE_FIREBASE_APP_ID
EOF
    
    echo -e "${GREEN}✓ .env.production created${NC}"
    cat .env.production
    echo ""
    
    echo -e "${YELLOW}Deploying frontend...${NC}"
    
    gcloud run deploy $FRONTEND_SERVICE \
        --source . \
        --region $REGION \
        --platform managed \
        --allow-unauthenticated \
        --port 80 \
        --memory 512Mi \
        --cpu 1 \
        --timeout 60 \
        --max-instances 5 \
        --min-instances 0
    
    # Clean up .env.production
    rm -f .env.production
    
    cd ..
    
    # Get frontend URL
    FRONTEND_URL=$(gcloud run services describe $FRONTEND_SERVICE \
        --region $REGION \
        --format 'value(status.url)')
    
    echo -e "${GREEN}✓ Frontend deployed at: $FRONTEND_URL${NC}\n"
}

# Parse command line arguments
case "${1:-both}" in
    backend)
        deploy_backend
        ;;
    frontend)
        deploy_frontend
        ;;
    both)
        deploy_backend
        deploy_frontend
        ;;
    *)
        echo "Usage: $0 {backend|frontend|both}"
        exit 1
        ;;
esac

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ Deployment Complete!${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Show service URLs
echo -e "${YELLOW}Service URLs:${NC}"
gcloud run services list --region $REGION --format="table(SERVICE,URL)"

echo -e "\n${YELLOW}Next Steps:${NC}"
echo "1. Update CORS settings in api/config/settings.py with frontend URL"
echo "2. Configure custom domain (optional)"
echo "3. Set up monitoring and alerts"
echo "4. Update Firebase authorized domains"

# Clean up
rm -f .backend_url
