FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY mcp_kroki_server.py .
COPY oauth_middleware.py .
COPY .env.example .env

# Expose port
EXPOSE 8084

# Run the server
CMD ["uvicorn", "mcp_kroki_server:app", "--host", "0.0.0.0", "--port", "8084"]
