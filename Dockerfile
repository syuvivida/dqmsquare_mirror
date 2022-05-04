FROM python:3.9

RUN apt update
RUN apt upgrade -y
# RUN apt remove -y imagemagick-6-common libaom0 libbluetooth-dev libbluetooth3 libapparmor1 libcairo2 libcairo2-dev 
# RUN apt remove -y libnss3 libopenjp2-7 mariadb-common libctf-nobfd0 libctf0
# RUN apt -y autoremove
RUN apt install -y firefox-esr 
RUN apt install -y nano iputils-ping sudo
 
ENV DEBIAN_FRONTEND noninteractive
ENV GECKODRIVER_VER v0.30.0
ENV FIREFOX_VER 91.2.0esr
ENV BOTTLE_VER 0.12.19

# Add latest FireFox
RUN set -x \
   && apt install -y \
       libx11-xcb1 \
       libdbus-glib-1-2 \
   && curl -sSLO https://download-installer.cdn.mozilla.net/pub/firefox/releases/${FIREFOX_VER}/linux-x86_64/en-US/firefox-${FIREFOX_VER}.tar.bz2 \
   && tar -jxf firefox-* \
   && mv firefox /opt/ \
   && chmod 755 /opt/firefox \
   && chmod 755 /opt/firefox/firefox
  
# Add geckodriver
RUN set -x \
   && curl -sSLO https://github.com/mozilla/geckodriver/releases/download/${GECKODRIVER_VER}/geckodriver-${GECKODRIVER_VER}-linux64.tar.gz \
   && tar zxf geckodriver-*.tar.gz \
   && mv geckodriver /usr/bin/

RUN apt install -y libnss3-tools

RUN mkdir -p /cephfs/testbed/dqmsquare_mirror/

ADD . /dqmsquare_mirror
WORKDIR dqmsquare_mirror
RUN python3 -m pip install -r requirements

# Add bottle
RUN set -x \
  && mkdir -p "bottle" \
  && cd "bottle" \
  && curl -sSLO https://github.com/bottlepy/bottle/archive/refs/tags/${BOTTLE_VER}.tar.gz \
  && tar -xvzf ${BOTTLE_VER}.tar.gz \
  && cp bottle-${BOTTLE_VER}/bottle.py .

# set CERN time zone
ENV TZ="Europe/Zurich"
RUN date

# add new user, add user to sudoers file, switch to user
RUN useradd 1000
RUN echo "%1000 ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
RUN mkdir -p /home/1000/
RUN chmod 777 /home/1000/
USER 1000
RUN sudo find /dqmsquare_mirror -type d -exec chmod 777 {} \; 
RUN sudo find /dqmsquare_mirror -type f -exec chmod 777 {} \;
 
CMD ["/bin/bash"]
