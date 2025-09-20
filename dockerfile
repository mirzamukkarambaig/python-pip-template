# Use Python Alpine base image
FROM python:3.11-alpine

# Set working directory
WORKDIR /app

# Install system dependencies that might be needed for Python packages
RUN apk add --no-cache \
    gcc \
    musl-dev \
    linux-headers \
    libffi-dev

# Copy requirements file
COPY requirements.txt .

# Upgrade pip and install Python dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy source code and configuration
COPY src/ ./src/
COPY tests/ ./tests/

# Create a non-root user for security
RUN addgroup -g 1001 -S appgroup && \
    adduser -S appuser -u 1001 -G appgroup

# Change ownership of the app directory
RUN chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# Expose port (adjust as needed)
EXPOSE 8000

# Default command - run the main application
CMD ["python", "-m", "src.app.main"]