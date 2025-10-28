# Use CentOS Stream as base
FROM centos:centos8

LABEL maintainer="svcansible@gmail.com"
LABEL description="Semaphore Pro Server on CentOS"

# Set environment variables
ENV SEMAPHORE_VERSION=2.16.18
ENV SEMAPHORE_HOME=/opt/semaphore
ENV SEMAPHORE_LOG_LEVEL=info

# Install dependencies
RUN dnf -y install \
      wget \
      unzip \
      git \
      python3 \
      python3-pip \
      mariadb-connector-c \
      iproute \
      curl \
      shadow-utils \
      && dnf clean all

# Create semaphore user and directories
RUN useradd -m -s /bin/bash semaphore && \
    mkdir -p ${SEMAPHORE_HOME}/config && \
    mkdir -p ${SEMAPHORE_HOME}/logs && \
    chown -R semaphore:semaphore ${SEMAPHORE_HOME}

# Download Semaphore Pro binary
# Replace this URL if you host it privately
RUN wget -O /usr/local/bin/semaphore \
    https://public.ecr.aws/semaphore/pro/releases/v${SEMAPHORE_VERSION}/linux_amd64/semaphore \
    && chmod +x /usr/local/bin/semaphore

# Copy configuration template (optional)
#COPY config.json ${SEMAPHORE_HOME}/config/config.json

# Expose default port
EXPOSE 3000

# Switch to semaphore user
USER semaphore
WORKDIR ${SEMAPHORE_HOME}

# Command to start Semaphore in debug mode
ENTRYPOINT ["/usr/local/bin/semaphore"]
CMD ["server", "--config", "/opt/semaphore/config/config.json", "--log-level", "debug"]