FROM node:18-alpine

# Install OpenSSL and other dependencies needed by Prisma
RUN apk add --no-cache openssl libc6-compat

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install all dependencies (including dev dependencies for build)
RUN npm install

# Copy source code
COPY . .

# Generate Prisma client
RUN npx prisma generate

# Build the application
RUN npm run build

# Remove dev dependencies for production
RUN npm prune --production

# Create non-root user
RUN addgroup -g 1001 -S nodejs
RUN adduser -S platform -u 1001

# Create logs directory
RUN mkdir -p /app/logs && chown -R platform:nodejs /app

# Switch to non-root user
USER platform

# Expose port
EXPOSE 9200

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
  CMD node dist/health.js || exit 1

# Start the application
CMD ["npm", "start"]