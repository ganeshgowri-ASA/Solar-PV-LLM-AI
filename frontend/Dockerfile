# =============================================================================
# Multi-stage Dockerfile for Solar PV LLM AI Frontend
# =============================================================================

# Stage 1: Build
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy source code
COPY . .

# Build application
RUN npm run build

# =============================================================================
# Stage 2: Production with Nginx
FROM nginx:1.25-alpine

# Install curl for health checks
RUN apk add --no-cache curl

# Copy custom nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder
COPY --from=builder /app/build /usr/share/nginx/html

# Create non-root user
RUN addgroup -g 1000 appuser && \
    adduser -D -u 1000 -G appuser appuser && \
    chown -R appuser:appuser /usr/share/nginx/html && \
    chown -R appuser:appuser /var/cache/nginx && \
    chown -R appuser:appuser /var/log/nginx && \
    chown -R appuser:appuser /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R appuser:appuser /var/run/nginx.pid

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost/ || exit 1

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
