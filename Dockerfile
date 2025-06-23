FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    openssh-client \
    procps \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create directory for logs and keys
RUN mkdir -p /app/logs /app/keys

# Set permissions
RUN chmod +x *.sh *.py

# Create non-root user for security
RUN useradd -m -u 1000 sshuser && chown -R sshuser:sshuser /app

# Switch to non-root user
USER sshuser

# Expose default SSH port
EXPOSE 2222

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import socket; s=socket.socket(); s.connect(('localhost', 2222)); s.close()" || exit 1

# Run the SSH server using the start script
CMD ["./start.sh"]
