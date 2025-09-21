# Project Minerva - Deployment Guide

This guide covers how to deploy Project Minerva to production environments.

## Prerequisites

- Google Cloud Project with the following APIs enabled:
  - Vertex AI API
  - BigQuery API
  - Cloud Storage API
  - Cloud Run API (for deployment)
- Node.js 18+ and Python 3.10+
- uv package manager
- Google Cloud SDK

## Environment Setup

### 1. Backend Configuration

Create a `.env` file in the `app/` directory:

```bash
# Google Cloud Configuration
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_CLOUD_LOCATION=us-central1

# BigQuery Configuration
BIGQUERY_DATASET=minerva_dataset
BIGQUERY_LOCATION=US

# Application Configuration
APP_ENV=production
SECRET_KEY=your-secure-secret-key
JWT_SECRET_KEY=your-secure-jwt-key
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=30

# File Upload Configuration
MAX_FILE_SIZE_MB=50
ALLOWED_FILE_TYPES=pdf,docx,pptx,xlsx,txt,md,png,jpg,jpeg

# Frontend Configuration
FRONTEND_URL=https://your-domain.com
BACKEND_URL=https://api.your-domain.com
```

### 2. Frontend Configuration

Create a `.env` file in the `frontend/` directory:

```bash
VITE_API_BASE_URL=https://api.your-domain.com
VITE_LANGGRAPH_URL=https://api.your-domain.com
```

## Local Development

### 1. Install Dependencies

```bash
# Install backend dependencies
uv sync

# Install frontend dependencies
npm --prefix frontend install
```

### 2. Setup BigQuery

```bash
# Create BigQuery dataset and tables
uv run python scripts/setup_bigquery.py
```

### 3. Run Development Servers

```bash
# Start both backend and frontend
make dev

# Or run separately
make dev-backend  # Backend on port 8000
make dev-frontend # Frontend on port 5173
```

## Production Deployment

### Option 1: Google Cloud Run (Recommended)

1. **Build and Deploy Backend:**

```bash
# Set your project
gcloud config set project YOUR_PROJECT_ID

# Deploy backend
gcloud run deploy minerva-backend \
  --source ./app \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars="GOOGLE_GENAI_USE_VERTEXAI=TRUE,APP_ENV=production"
```

2. **Build and Deploy Frontend:**

```bash
# Build frontend
npm --prefix frontend run build

# Deploy to Cloud Run
gcloud run deploy minerva-frontend \
  --source ./frontend \
  --region us-central1 \
  --allow-unauthenticated
```

### Option 2: Docker Deployment

1. **Backend Dockerfile:**

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY app/ ./app/
EXPOSE 8000

CMD ["uv", "run", "adk", "api_server", "app", "--host", "0.0.0.0", "--port", "8000"]
```

2. **Frontend Dockerfile:**

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci

COPY frontend/ ./
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Option 3: Kubernetes

Use the provided Kubernetes manifests in the `k8s/` directory:

```bash
kubectl apply -f k8s/
```

## Database Setup

### BigQuery Schema

The application automatically creates the following tables:

- `startups` - Startup submission data
- `analyses` - Analysis results
- `users` - User accounts
- `teams` - Team information
- `comments` - User comments
- `agent_traces` - Agent execution traces
- `sources` - Source citations

### Data Migration

For existing data migration:

```bash
uv run python scripts/migrate_data.py
```

## Security Configuration

### 1. Authentication

- Configure JWT secrets in production
- Set up proper CORS origins
- Enable HTTPS for all endpoints

### 2. API Security

- Rate limiting is enabled by default
- File upload size limits are enforced
- Input validation on all endpoints

### 3. Data Privacy

- All PII is encrypted at rest
- Audit logging is enabled
- GDPR compliance features included

## Monitoring and Logging

### 1. Application Monitoring

- Health checks available at `/health`
- Metrics endpoint at `/metrics`
- Structured logging to Cloud Logging

### 2. Performance Monitoring

- Agent execution tracing
- Database query performance
- File upload monitoring

## Scaling Considerations

### 1. Backend Scaling

- Horizontal scaling with Cloud Run
- Connection pooling for BigQuery
- Async processing for long-running analyses

### 2. Frontend Scaling

- CDN for static assets
- Caching strategies
- Progressive loading

## Troubleshooting

### Common Issues

1. **BigQuery Connection Issues:**
   - Verify service account permissions
   - Check dataset location settings
   - Ensure APIs are enabled

2. **Agent Execution Failures:**
   - Check Vertex AI quotas
   - Verify model availability
   - Review agent configuration

3. **File Upload Problems:**
   - Check Cloud Storage permissions
   - Verify file size limits
   - Review MIME type restrictions

### Debug Mode

Enable debug logging:

```bash
export LOG_LEVEL=DEBUG
export ENABLE_AGENT_TRACING=true
```

## Backup and Recovery

### 1. Data Backup

BigQuery data is automatically backed up. For additional backups:

```bash
# Export BigQuery data
bq extract --destination_format=AVRO \
  minerva_dataset.startups \
  gs://your-backup-bucket/startups_backup.avro
```

### 2. Configuration Backup

- Store environment variables in Secret Manager
- Version control all configuration files
- Document all manual configuration steps

## Support

For deployment issues:

1. Check the [troubleshooting guide](docs/troubleshooting.md)
2. Review [ADK documentation](https://google.github.io/adk-docs/)
3. Contact support at support@projectminerva.ai

## Security Checklist

- [ ] All secrets stored in Secret Manager
- [ ] HTTPS enabled for all endpoints
- [ ] CORS properly configured
- [ ] Rate limiting enabled
- [ ] Input validation implemented
- [ ] Audit logging configured
- [ ] Backup strategy implemented
- [ ] Monitoring and alerting set up
