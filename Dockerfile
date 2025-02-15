# Base image
FROM python:3.12-slim-bookworm

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates nodejs npm git \
    && rm -rf /var/lib/apt/lists/*

# Download and install uv
ADD https://astral.sh/uv/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"

# Install Python dependencies using uv

# Install Prettier globally
RUN npm install -g prettier@3.4.2


# Set working directory
WORKDIR /app
RUN mkdir -p /data

# Copy application files
COPY app.py /app

# Set the correct Git executable path for GitPython
ENV GIT_PYTHON_GIT_EXECUTABLE=/usr/bin/git

# Start the application
CMD ["uv", "run", "app.py"]
