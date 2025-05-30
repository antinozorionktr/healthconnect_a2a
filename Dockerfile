# Hospital A2A Appointment Booking System
# Multi-stage Docker build for Python 3.13

FROM python:3.13-slim as base

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PIP_NO_CACHE_DIR=1
ENV PIP_DISABLE_PIP_VERSION_CHECK=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    supervisor \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY hospital_a2a_system.py .
COPY frontend.py .

# Create logs directory
RUN mkdir -p /var/log/supervisor

# Create supervisor configuration
RUN echo '[supervisord]' > /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'nodaemon=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'user=root' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'logfile=/var/log/supervisor/supervisord.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'pidfile=/var/run/supervisord.pid' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '[program:coordinator]' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'command=python hospital_a2a_system.py coordinator' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile=/var/log/supervisor/coordinator.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stderr_logfile=/var/log/supervisor/coordinator_error.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_backups=3' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '[program:patient]' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'command=python hospital_a2a_system.py patient' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile=/var/log/supervisor/patient.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stderr_logfile=/var/log/supervisor/patient_error.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_backups=3' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '[program:doctor]' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'command=python hospital_a2a_system.py doctor' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile=/var/log/supervisor/doctor.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stderr_logfile=/var/log/supervisor/doctor_error.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_backups=3' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '[program:booking]' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'command=python hospital_a2a_system.py booking' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile=/var/log/supervisor/booking.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stderr_logfile=/var/log/supervisor/booking_error.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_backups=3' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo '[program:frontend]' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'command=streamlit run frontend.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'directory=/app' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autostart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'autorestart=true' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile=/var/log/supervisor/frontend.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stderr_logfile=/var/log/supervisor/frontend_error.log' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_maxbytes=10MB' >> /etc/supervisor/conf.d/hospital_a2a.conf && \
    echo 'stdout_logfile_backups=3' >> /etc/supervisor/conf.d/hospital_a2a.conf

# Create startup script for proper initialization
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'echo "🏥 Starting Hospital A2A Appointment Booking System..."' >> /app/start.sh && \
    echo 'echo "="*60' >> /app/start.sh && \
    echo 'echo "Starting agents in sequence..."' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start coordinator first' >> /app/start.sh && \
    echo 'echo "🚀 Starting Coordinator Agent (Port 8000)..."' >> /app/start.sh && \
    echo 'supervisorctl start coordinator' >> /app/start.sh && \
    echo 'sleep 2' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start specialized agents' >> /app/start.sh && \
    echo 'echo "👤 Starting Patient Registration Agent (Port 8001)..."' >> /app/start.sh && \
    echo 'supervisorctl start patient' >> /app/start.sh && \
    echo 'sleep 2' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'echo "🩺 Starting Doctor Availability Agent (Port 8002)..."' >> /app/start.sh && \
    echo 'supervisorctl start doctor' >> /app/start.sh && \
    echo 'sleep 2' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'echo "📅 Starting Appointment Booking Agent (Port 8003)..."' >> /app/start.sh && \
    echo 'supervisorctl start booking' >> /app/start.sh && \
    echo 'sleep 2' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Start frontend last' >> /app/start.sh && \
    echo 'echo "🌐 Starting Streamlit Frontend (Port 8501)..."' >> /app/start.sh && \
    echo 'supervisorctl start frontend' >> /app/start.sh && \
    echo 'sleep 3' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo 'echo "✅ All services started successfully!"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo 'echo "🌐 Access the system at:"' >> /app/start.sh && \
    echo 'echo "  Frontend: http://localhost:8501"' >> /app/start.sh && \
    echo 'echo "  Coordinator API: http://localhost:8000"' >> /app/start.sh && \
    echo 'echo "  Patient Service: http://localhost:8001"' >> /app/start.sh && \
    echo 'echo "  Doctor Service: http://localhost:8002"' >> /app/start.sh && \
    echo 'echo "  Booking Service: http://localhost:8003"' >> /app/start.sh && \
    echo 'echo ""' >> /app/start.sh && \
    echo 'echo "📊 Monitor logs with:"' >> /app/start.sh && \
    echo 'echo "  supervisorctl status"' >> /app/start.sh && \
    echo 'echo "  tail -f /var/log/supervisor/*.log"' >> /app/start.sh && \
    echo '' >> /app/start.sh && \
    echo '# Keep container running' >> /app/start.sh && \
    echo 'supervisord -c /etc/supervisor/conf.d/hospital_a2a.conf' >> /app/start.sh && \
    chmod +x /app/start.sh

# Create health check script
RUN echo '#!/bin/bash' > /app/healthcheck.sh && \
    echo '# Health check for all services' >> /app/healthcheck.sh && \
    echo '' >> /app/healthcheck.sh && \
    echo '# Check if all agents are responding' >> /app/healthcheck.sh && \
    echo 'coordinator_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/.well-known/agent.json)' >> /app/healthcheck.sh && \
    echo 'patient_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8001/.well-known/agent.json)' >> /app/healthcheck.sh && \
    echo 'doctor_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8002/.well-known/agent.json)' >> /app/healthcheck.sh && \
    echo 'booking_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8003/.well-known/agent.json)' >> /app/healthcheck.sh && \
    echo 'frontend_status=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8501)' >> /app/healthcheck.sh && \
    echo '' >> /app/healthcheck.sh && \
    echo 'if [ "$coordinator_status" = "200" ] && [ "$patient_status" = "200" ] && [ "$doctor_status" = "200" ] && [ "$booking_status" = "200" ] && [ "$frontend_status" = "200" ]; then' >> /app/healthcheck.sh && \
    echo '    exit 0' >> /app/healthcheck.sh && \
    echo 'else' >> /app/healthcheck.sh && \
    echo '    echo "Health check failed. Status codes: coordinator=$coordinator_status, patient=$patient_status, doctor=$doctor_status, booking=$booking_status, frontend=$frontend_status"' >> /app/healthcheck.sh && \
    echo '    exit 1' >> /app/healthcheck.sh && \
    echo 'fi' >> /app/healthcheck.sh && \
    chmod +x /app/healthcheck.sh

# Expose all required ports
EXPOSE 8000 8001 8002 8003 8501

# Add health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD /app/healthcheck.sh

# Set the startup command
CMD ["/app/start.sh"]

# Labels for metadata
LABEL maintainer="Hospital A2A System"
LABEL version="1.0.0"
LABEL description="Hospital Appointment Booking System using A2A Protocol"
LABEL org.opencontainers.image.source="https://github.com/your-org/hospital-a2a"
LABEL org.opencontainers.image.title="Hospital A2A System"
LABEL org.opencontainers.image.description="Distributed hospital appointment booking system using Google's A2A protocol"
LABEL org.opencontainers.image.version="1.0.0"