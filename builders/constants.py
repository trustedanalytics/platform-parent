#
# Copyright (c) 2015 Intel Corporation
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

import os
import multiprocessing

# Reading number of processors due to creating threads per processor which runs subprocess commands
CPU_CORES_COUNT = multiprocessing.cpu_count()

ATK_REPOS_URL = 'https://analytics-tool-kit.s3-us-west-2.amazonaws.com/public/weekly/regressed/'
TAP_REPOS_URL = 'https://github.com/trustedanalytics/'
GEARPUMP_BINARIES_URL = 'https://github.com/gearpump/gearpump/releases/download/{short_ver}/gearpump-{long_ver}.zip'

LATEST_ATK_VERSION = 'latest'
DEFAULT_ATK_VERSION = LATEST_ATK_VERSION

PLATFORM_PARENT_PATH = os.getcwd()
APPS_YAML_FILE_PATH = 'cloud_apps.yml'
DEFAULT_DESTINATION_PATH = '/tmp/TAP_PACKAGES'
