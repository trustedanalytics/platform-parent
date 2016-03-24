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
import yaml
from lib.logger import LOGGER

# constants - change only for development
PLATFORM_PARENT_PATH = os.getcwd()
ATK_REPOS_URL = 'https://analytics-tool-kit.s3-us-west-2.amazonaws.com/public/weekly/regressed/'
TAP_REPOS_URL = 'https://github.com/trustedanalytics/'
GEARPUMP_BINARIES_URL = 'https://github.com/gearpump/gearpump/releases/download/{short_ver}/gearpump-{long_ver}.zip'
LATEST_ATK_VERSION = 'latest'
APPS_YAML_FILE_PATH = 'cloud_apps.yml'

try:
    with open(os.path.join(PLATFORM_PARENT_PATH, 'config.yml'), 'r') as stream:
        user_conf = yaml.load(stream)
except Exception as e:
    LOGGER.error('Cannot read config.yml file.')
    raise e

# constants loaded from config.yml file
ATK_VERSION = user_conf['ATK_VERSION']
TARGET_CATALOG_NAME = user_conf['TARGET_CATALOG_NAME']
DESTINATION_ABS_PATH = user_conf['DESTINATION_ABS_PATH']
RELEASE_TAG = user_conf['RELEASE_TAG']
