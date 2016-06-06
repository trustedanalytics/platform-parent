#!/bin/bash
#
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


get_maven_proxy_settings() {
# Usage: get_maven_proxy_settings HTTP_PROXY
# Returns: Maven settings.xml proxy configuration created according to HTTP_PROXY parameter
mvn_http_proxy=$1

# Parse Maven proxy configuration fields
mvn_proxy_protocol=$(echo $mvn_http_proxy | cut -d ':' -f 1)
mvn_proxy_host=$(echo $mvn_http_proxy | cut -d ':' -f 2 | sed 's#//##')
mvn_proxy_port=$(echo $mvn_http_proxy | cut -d ':' -f 3)
  
read -d '' mvn_proxy_configuration <<EOF

<proxies>
  <proxy>
    <id>proxy-configuration</id>
    <active>true</active>
    <protocol>$mvn_proxy_protocol</protocol>
    <host>$mvn_proxy_host</host>
    <port>$mvn_proxy_port</port>
  </proxy>
</proxies>

EOF

 echo $mvn_proxy_configuration
  
}

echo_run_usage() {
  echo "Usage: build_tap.sh run PLATFORM_PARENT_PATH ARTIFACTS_OUTPUT_PATH [platform-parent arguments]."
}

# Exit immediately on any error.
set -e

if [[ -z "$1" ]] || [[ "$1" = "-h" ]] || [[ "$1" = "--help" ]]; then
  echo -e "Usage: build_tap.sh (build|run) \n"
  echo -e "In order to build platform-parent Docker image run: build_tap.sh build. \n"
  echo -e "In order to start platform-parent Docker container run: build_tap.sh run PLATFORM_PARENT_PATH ARTIFACTS_OUTPUT_PATH, where:\n PLATFORM_PARENT_PATH - points to platform-parent directory on host machine\n ARTIFACTS_OUTPUT_PATH - points to directory on host machine, where artifacts produced by platform-parent will be stored."
  echo -e "Script checks http_proxy, https_proxy, HTTP_PROXY and HTTPS_PROXY environment variables in order to determine your proxy configuration and propagates proxy environment variables and Maven proxy settings on Docker image."
  exit 1
fi

COMMAND=$1
if [[ "$COMMAND" != "build" ]] && [[ "$COMMAND" != "run" ]]; then
  echo "Pass proper command (build|run) as first argument."
fi

# Get local http_proxy settings
if [ -z "$local_http_proxy" ]; then

  if [ -n "$HTTP_PROXY" ]; then
    local_http_proxy="$HTTP_PROXY"
  fi

  if [ -n "$http_proxy" ]; then
    local_http_proxy="$http_proxy"
  fi

fi

# Get local https_proxy settings
if [ -z "$local_https_proxy" ]; then

  if [ -n "$HTTPS_PROXY" ]; then
    local_https_proxy="$HTTPS_PROXY"
  fi

  if [ -n "$https_proxy" ]; then
    local_https_proxy="$https_proxy"
  fi

  # If https_proxy is not set, use http_proxy value for https_proxy
  if [ -z "$https_proxy" ]; then
    local_https_proxy="$local_http_proxy"
  fi

fi

if [ "$COMMAND" = "build" ]; then

  if [[ -n "$local_http_proxy" ]] && [[ -n "$local_https_proxy" ]]; then
    echo -e "Detected proxy settings: \n http proxy: $local_http_proxy \n https proxy: $local_https_proxy"
    # Build image with configured proxy settings
    # Set correct proxy environment variables in Dockerfile
    PROXY_DOCEKRFILE_TEMPLATE='Dockerfile_proxy_template'
    PROXY_DOCKERFILE='Dockerfile_proxy'
    cp "$PROXY_DOCEKRFILE_TEMPLATE" "$PROXY_DOCKERFILE"
    sed -i -e "s#<HTTP_PROXY>#$local_http_proxy#g" "$PROXY_DOCKERFILE"
    sed -i -e "s#<HTTPS_PROXY>#$local_https_proxy#g" "$PROXY_DOCKERFILE"

    # Create settings_proxy.xml file with properly configured proxy settings
    MAVEN_SETTINGS_FILE='settings.xml'
    MAVEN_PROXY_SETTINGS_FILE='settings_proxy.xml'
    MAVEN_PROXY_SETTINGS=$(get_maven_proxy_settings $local_http_proxy)    
    cp "$MAVEN_SETTINGS_FILE" "$MAVEN_PROXY_SETTINGS_FILE"
    sed -i '/<profiles>/i\'"$MAVEN_PROXY_SETTINGS" "$MAVEN_PROXY_SETTINGS_FILE"

    # Building base image
    echo  "Running: docker build --build-arg http_proxy=$local_http_proxy --build-arg https_proxy=$local_https_proxy -f Dockerfile -t platform-parent ."
    docker build --build-arg http_proxy=$local_http_proxy --build-arg https_proxy=$local_https_proxy -f Dockerfile -t platform-parent .

    # Build docker image with configured proxy
    echo  "Running: docker build --build-arg http_proxy=$local_http_proxy --build-arg https_proxy=$local_https_proxy -f Dockerfile_proxy -t platform-parent ."
    docker build  --build-arg http_proxy=$local_http_proxy --build-arg https_proxy=$local_https_proxy -f Dockerfile_proxy -t platform-parent .

  else
    # Build image without proxy configuration
    # Building base image
    echo  'Running: docker build -f Dockerfile -t platform-parent .'
    docker build -f Dockerfile -t platform-parent .
  fi
 
  exit 0
fi

if [ "$COMMAND" = "run" ]; then
  
  PLATFORM_PARENT_PATH=$2
  ARTIFACTS_OUTPUT_PATH=$3
  
  if [[ -z "$2" ]] || [[ "$2" = "-h" ]] || [[ "$2" = "--help" ]]; then
    echo_run_usage
    exit 1
  fi

  if [[ -z "$PLATFORM_PARENT_PATH" ]] || [[ -z "$ARTIFACTS_OUTPUT_PATH" ]]; then
    echo_run_usage
    exit 1
  fi

  if [[ ! -d "$PLATFORM_PARENT_PATH" ]]; then
    echo "Pass existing directory as PLATFORM_PARENT_PATH."
    exit 1
  fi

  if [[ ! -d "$ARTIFACTS_OUTPUT_PATH" ]]; then
    echo "Pass existing directory as ARTIFACTS_OUTPUT_PATH."
    exit 1
  fi

  echo "Running docker run -i -v $PLATFORM_PARENT_PATH:/platform-parent -v $ARTIFACTS_OUTPUT_PATH:/artifacts -t platform-parent python build_platform.py -d /artifacts ${@:4}"
  
  docker run -i -v $PLATFORM_PARENT_PATH:/platform-parent -v $ARTIFACTS_OUTPUT_PATH:/artifacts -t platform-parent python build_platform.py -d /artifacts ${@:4}

  exit 0
fi

