FROM ppodgorsek/robot-framework:3.3.1 

ARG FFMPEG_VERSION="4.2.1"
ARG FFMPEG_ARCH="amd64"

## Install SSH server
# RUN yum update -y --enableplugin fastestmirror # too slow

RUN yum install --enableplugin fastestmirror -y openssh-server.x86_64 xorg-x11-xauth.x86_64 xorg-x11-apps.x86_64 python3-tkinter.x86_64 xz jq ImageMagick.x86_64 &&\
    head -c 64 /dev/urandom | ssh-keygen -q -N "" -t ed25519 -f /etc/ssh/ssh_host_ed25519_key -a 10000 &&\
    ssh-keygen -q -P "" -t ed25519 -f /root/.ssh/robot_manual_test_key -a 1000 &&\
    cat /root/.ssh/robot_manual_test_key.pub >> /root/.ssh/authorized_keys &&\
    chmod 700 /root/.ssh && chmod 600 /root/.ssh/authorized_keys && mkdir -p /var/run/sshd &&\
    curl -o /tmp/ffmpeg.tar.xz https://johnvansickle.com/ffmpeg/old-releases/ffmpeg-${FFMPEG_VERSION}-${FFMPEG_ARCH}-static.tar.xz &&\
    tar -xf /tmp/ffmpeg.tar.xz &&\
    mv ffmpeg-${FFMPEG_VERSION}-${FFMPEG_ARCH}-static/ffmpeg ffmpeg-${FFMPEG_VERSION}-${FFMPEG_ARCH}-static/ffprobe /usr/bin &&\
    rm -rf /tmp/ffmpeg.tar.xz ffmpeg-${FFMPEG_VERSION}-${FFMPEG_ARCH}-static

### Uncomment following two lines if having external test libraries:
COPY requirements.txt .
RUN dnf install --setopt=install_weak_deps=False --assumeyes git python3-tkinter tk-devel android-tools npm xcompmgr &&\
    npm install -g appium --unsafe-perm=true --allow-root &&\
    pip3 install --upgrade pip &&\
    python3 -m pip install --no-cache-dir -r requirements.txt

COPY docker/bin/chromedriver.sh /opt/robotframework/bin/chromedriver
COPY docker/bin/entrypoint.sh /opt/robotframework/bin/entrypoint.sh
COPY docker/bin/run_tests_no_fb.sh /opt/robotframework/bin/run_tests_no_fb.sh

RUN chmod 777 -R /opt/robotframework/bin &&\
    chmod 777 -R /opt/robotframework/drivers &&\
    mkdir -p /home/user &&\
    chmod 777 -R /home/user &&\    
    mkdir -p /opt/robotframework/artifact_store &&\
    chmod 777 -R /opt/robotframework/artifact_store 


    
CMD [ "entrypoint.sh" ]
