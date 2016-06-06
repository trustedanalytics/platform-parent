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

FROM debian:jessie

# Java
RUN apt-get update && apt-get install -y \
    software-properties-common=0.92.25debian1 \
    python-software-properties=0.92.25debian1 && \
   echo "deb http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" > /etc/apt/sources.list.d/webupd8team-java.list && \
   echo "deb-src http://ppa.launchpad.net/webupd8team/java/ubuntu trusty main" >> /etc/apt/sources.list.d/webupd8team-java.list && \
   apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys EEA14886 && \
   echo oracle-java8-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
  apt-get update && yes | apt-get install -y \
    oracle-java8-installer \
    oracle-java8-set-default

# Maven
RUN apt-get install -y maven=3.0.5-3

# Node.js
RUN apt-get install -y nodejs=0.10.29~dfsg-2 npm=1.4.21+ds-2 && ln -s /usr/bin/nodejs /usr/bin/node

# Python
RUN apt-get install -y \
  python=2.7.9-1 \
  python-dev=2.7.9-1 \
  python-setuptools=5.5.1-1 \
  python-pip=1.5.6-5 \
  python3-pip=1.5.6-5

# pip packages
RUN pip install \
  pyyaml==3.11 \
  tox==2.3.1 \
  virtualenv==15.0.1

# upgrade pip
RUN pip install -U pip setuptools

# Git
RUN apt-get install -y git=1:2.1.4-2.1+deb8u2 && git config --global url."https://".insteadOf git://

# FFI lib
RUN apt-get install -y libffi-dev=3.1-2+b2

# GO
RUN wget https://storage.googleapis.com/golang/go1.6.linux-amd64.tar.gz -O golang.tar.gz && \
  tar -xvf golang.tar.gz -C /usr/local && \
  mkdir ~/go-workspace && \
  echo 'export GOPATH=$HOME/go-workspace' >> /root/.bashrc && echo 'export GOPATH=$HOME/go-workspace' >> /root/.profile

ENV PATH=/usr/local/go/bin:$HOME/go-workspace/bin:$PATH
ENV GOPATH=$HOME/go-workspace

RUN /bin/bash -c "go get github.com/tools/godep"

# Ruby
RUN apt-get install -y curl=7.38.0-4+deb8u3 && \
  gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 && \
  curl -L https://get.rvm.io | bash -s stable && \
  /bin/bash -c "source /etc/profile.d/rvm.sh && rvm install ruby-2.1.5 && rvm use 2.1.5" && \
  /bin/bash -c "source /etc/profile.d/rvm.sh && gem install compass && gem install cf-uaac" && \
  echo "source /etc/profile.d/rvm.sh" >> /root/.bashrc && echo "source /etc/profile.d/rvm.sh" >> /root/.profile

# Set locale to en_US.UTF-8 (avoid problems with compilation of files containing non-ASCII characters)
ENV LC_ALL=C.UTF-8 LANG=C.UTF-8 LANGUAGE=C.UTF-8

# Install libfontconfig package - phantomjs (console dependency) depends on this package
RUN apt-get install -y libfontconfig1=2.11.0-6.3

# Install zip
RUN apt-get install -y zip=3.0-8

# Copy settings.xml file
COPY settings.xml /usr/share/maven/conf/settings.xml

# Create platform-parent and artifact output volumes
RUN mkdir /platform-parent && mkdir /artifacts
VOLUME /platform-parent /artifacts

# Set working directory and entrypoint
WORKDIR /platform-parent
