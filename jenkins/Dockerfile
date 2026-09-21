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

# Add Jenkins to the Docker socket group so it can access the Docker daemon.
RUN usermod -aG root jenkins

USER jenkins
