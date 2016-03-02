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
    software-properties-common \
    python-software-properties && \
  add-apt-repository ppa:chris-lea/node.js && \
  add-apt-repository ppa:webupd8team/java && \
  apt-get update && yes | apt-get install -y \
    oracle-java8-installer \
    oracle-java8-set-default

# Maven
RUN apt-get install -y maven

# Node.js
RUN apt-get install -y nodejs

# Python
RUN apt-get install -y \
  python \
  python-dev \
  python-setuptools \
  python-pip

# pip packages
RUN pip install \
  pyyaml \
  tox \
  virtualenv

# upgrade pip
RUN pip install -U pip setuptools

# Git
RUN apt-get install -y git

# FFI lib
RUN apt-get install -y libffi-dev

# GO
RUN apt-get install -y \
    bison \
    curl && \
  curl -s -S -L https://raw.githubusercontent.com/moovweb/gvm/master/binscripts/gvm-installer | bash && \
  /bin/bash -c "source /root/.gvm/scripts/gvm && gvm install go1.4.2 && gvm use go1.4.2 && go get github.com/tools/godep" && \
  apt-get install -y gccgo-go && \
  mkdir ~/go-workspace && \
  echo "gvm use go1.4.2" >> /root/.bashrc && \
  echo 'export GOPATH=$HOME/go-workspace' >> /root/.bashrc

ENV PATH $PATH:$GOPATH/bin

# Ruby
RUN \
  gpg --keyserver hkp://keys.gnupg.net --recv-keys 409B6B1796C275462A1703113804BB82D39DC0E3 && \
  curl -L https://get.rvm.io | bash -s stable && \
  /bin/bash -c "source /etc/profile.d/rvm.sh && rvm install ruby-2.1.5 && rvm use 2.1.5" && \
  /bin/bash -c "source /etc/profile.d/rvm.sh && gem install compass && gem install cf-uaac" && \
  echo "source /etc/profile.d/rvm.sh" >> /root/.bashrc

# Set locale to en_US.UTF-8 (avoid problems with compilation of files containing non-ASCII characters)
RUN locale-gen en_US.UTF-8 && dpkg-reconfigure locales
ENV LC_ALL=en_US.UTF-8 LANG=en_US.UTF-8

# Install libfontconfig package - phantomjs (console dependency) depends on this package
RUN apt-get install -y libfontconfig

# Install zip
RUN apt-get install -y zip

# Copy settings.xml file
COPY settings.xml /usr/share/maven/conf/settings.xml

# Install tmux and vim for convenience
RUN apt-get install -y \
  tmux \
  vim

# Clone platform parent
RUN git clone https://github.com/trustedanalytics/platform-parent.git /root/platform-parent
