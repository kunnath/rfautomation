# Use AlmaLinux 8 as a base image
FROM almalinux:8

# Set environment variables
ENV ROBOT_VERSION=4.0
ENV PYTHONUNBUFFERED=1

# Update and install required packages
RUN yum update -y && \
    yum install -y epel-release && \
    yum config-manager --enable epel && \
    yum install -y \
    python3 \
    python3-pip \
    openssh-server \
    xorg-x11-xauth \
    jq \
    git \
    which && \
    yum clean all

# Install Node.js 20+ for npm compatibility
RUN curl -fsSL https://rpm.nodesource.com/setup_20.x | bash - && \
    yum install -y nodejs && \
    npm install -g npm@latest --unsafe-perm=true && \
    npm cache clean --force && \
    yum clean all

# Additional configurations remain unchanged
COPY requirements.txt .
RUN dnf install --setopt=install_weak_deps=False --assumeyes \
    git \
    python3-tkinter \
    tk-devel \
    android-tools \
    xcompmgr && \
    npm install -g appium --unsafe-perm=true --allow-root && \
    pip3 install --upgrade pip && \
    python3 -m pip install --no-cache-dir -r requirements.txt 

# Set permissions and copy necessary scripts
COPY docker/bin/chromedriver.sh /opt/robotframework/bin/chromedriver
COPY docker/bin/entrypoint.sh /opt/robotframework/bin/entrypoint.sh
COPY docker/bin/run_tests_no_fb.sh /opt/robotframework/bin/run_tests_no_fb.sh

# Set permissions and create necessary directories
RUN mkdir -p /opt/robotframework/drivers && \
    chmod 777 -R /opt/robotframework/bin && \
    chmod 777 -R /opt/robotframework/drivers && \
    mkdir -p /home/user && \
    chmod 777 -R /home/user && \
    mkdir -p /opt/robotframework/artifact_store && \
    chmod 777 -R /opt/robotframework/artifact_store 

RUN chmod +x /opt/robotframework/bin/entrypoint.sh

CMD [ "/opt/robotframework/bin/entrypoint.sh" ]