# Frontend Dockerfile for Project Younicorn - Multi-stage build
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including devDependencies needed for build)
RUN npm ci

# Copy source code
COPY . .

# Vite will automatically load .env.production during build
# Verify .env.production exists and show its contents for debugging
RUN echo "=== Checking for .env.production ===" && \
    if [ -f .env.production ]; then \
        echo "✓ .env.production found:" && \
        cat .env.production; \
    else \
        echo "✗ .env.production NOT FOUND - using defaults"; \
    fi

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy built files from builder
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost/health || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
