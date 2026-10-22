FROM jenkins/jenkins:lts-jdk17

USER root

# Install Python tools required to create the CI virtual environment
# and run the project's automated tests.
RUN apt-get update \
    && apt-get install -y python3 python3-pip python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI so Jenkins can build and manage Docker images.
RUN apt-get update \
    && apt-get install -y docker.io \
    && rm -rf /var/lib/apt/lists/*

# Install curl because Docker Compose is downloaded directly
# from the official Docker Compose release.
RUN apt-get update \
    && apt-get install -y curl \
    && rm -rf /var/lib/apt/lists/*

# Install Docker Compose v2 as a Docker CLI plugin.
# This allows Jenkins to run commands such as:
# docker compose up
# docker compose down
RUN mkdir -p /usr/local/lib/docker/cli-plugins \
    && curl -SL \
       https://github.com/docker/compose/releases/download/v2.35.1/docker-compose-linux-x86_64 \
       -o /usr/local/lib/docker/cli-plugins/docker-compose \
    && chmod +x /usr/local/lib/docker/cli-plugins/docker-compose

# Add Jenkins to the Docker socket group so it can access the Docker daemon.
RUN usermod -aG root jenkins

USER jenkins