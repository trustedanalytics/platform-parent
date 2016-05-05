# Copyright (c) 2016 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

FROM ubuntu:14.04

# Java
RUN apt-get update && apt-get install -y \
    software-properties-common=0.92.37.7 \
    python-software-properties=0.92.37.7 && \
  add-apt-repository ppa:chris-lea/node.js && \
  add-apt-repository ppa:webupd8team/java && \
  apt-get update && yes | apt-get install -y \
    oracle-java8-installer \
    oracle-java8-set-default

# Maven
RUN apt-get install -y maven=3.0.5-1

# Node.js
RUN apt-get install -y nodejs=0.10.37-1chl1~trusty1

# Python
RUN apt-get install -y \
  python=2.7.5-5ubuntu3 \
  python-dev=2.7.5-5ubuntu3 \
  python-setuptools=3.3-1ubuntu2 \
  python-pip=1.5.4-1ubuntu3

# pip packages
RUN pip install \
  pyyaml==3.11 \
  tox==2.3.1 \
  virtualenv==15.0.0

# upgrade pip
RUN pip install -U pip setuptools

# Git
RUN apt-get install -y git=1:1.9.1-1ubuntu0.3

# FFI lib
RUN apt-get install -y libffi-dev=3.1~rc1+r3.0.13-12ubuntu0.1

# GO
RUN apt-get install -y \
    bison=2:3.0.2.dfsg-2 \
    curl=7.35.0-1ubuntu2.6 && \
  curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer | bash && \
  /bin/bash -c "source /root/.gvm/scripts/gvm && gvm install go1.4.2 && gvm use go1.4.2 && go get github.com/tools/godep" && \
  apt-get install -y gccgo-go=1.2.1-0ubuntu1.2 && \
  mkdir ~/go-workspace && \
  echo '[[ -s "/root/.gvm/scripts/gvm" ]] && source "/root/.gvm/scripts/gvm"' >> /root/.profile && \
  echo "gvm use go1.4.2" >> /root/.bashrc && echo "gvm use go1.4.2" >> /root/.profile \
  echo 'export GOPATH=$HOME/go-workspace' >> /root/.bashrc && echo 'export GOPATH=$HOME/go-workspace' >> /root/.profile

ENV PATH $PATH:$GOPATH/bin

# Ruby
RUN \
  gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 && \
  curl -L https://get.rvm.io | bash -s stable && \
  /bin/bash -c "source /etc/profile.d/rvm.sh && rvm install ruby-2.1.5 && rvm use 2.1.5" && \
  /bin/bash -c "source /etc/profile.d/rvm.sh && gem install compass && gem install cf-uaac" && \
  echo "source /etc/profile.d/rvm.sh" >> /root/.bashrc && echo "source /etc/profile.d/rvm.sh" >> /root/.profile

# Set locale to en_US.UTF-8 (avoid problems with compilation of files containing non-ASCII characters)
RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales
ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# Install libfontconfig package - phantomjs (console dependency) depends on this package
RUN apt-get install -y libfontconfig1=2.11.0-0ubuntu4.1

# Install zip
RUN apt-get install -y zip=3.0-8

# Copy settings.xml file
COPY settings.xml /usr/share/maven/conf/settings.xml

# Install tmux and vim for convenience
RUN apt-get install -y \
  tmux=1.8-5 \
  vim=2:7.4.052-1ubuntu3

# Create platform-parent and artifact output volumes
RUN mkdir /platform-parent && mkdir /artifacts
VOLUME /platform-parent /artifacts

# Set working directory and entrypoint
WORKDIR /platform-parent
ENTRYPOINT [ "/bin/bash", "-l", "-c", "gvm use go1.4.2 && python build_platform.py -d /artifacts"]
