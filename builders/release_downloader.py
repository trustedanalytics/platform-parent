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
import subprocess

from constants import PLATFORM_PARENT_PATH
from constants import TAP_REPOS_URL
from lib.logger import LOGGER

class ReleaseDownloader:

    def __init__(self, app_info):
        self.name = app_info['name']
        self.snapshot = app_info.get('snapshot')
        self.url = app_info.get('url')
        self.sources_path = os.path.join(PLATFORM_PARENT_PATH, self.name)
        self.zip_name = '{}.zip'.format(app_info.get('zip_name', self.name))
        self.logs_directory_path = os.path.join(PLATFORM_PARENT_PATH, 'logs')
        if not os.path.exists(self.logs_directory_path):
            os.makedirs(self.logs_directory_path)
        self.build_log_path = os.path.join(self.logs_directory_path, self.name + '-build.log')
        self.err_log_path = os.path.join(self.logs_directory_path, self.name + '-err.log')

    def download_release_zip(self, dest_path):
        if not self.url:
            LOGGER.error('Not specified release url for %s', self.name)
            raise 'Not specified release url for {}'.format(self.name)
        LOGGER.info('Downloading release package for %s from %s', self.name, self.url)
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            try:
                subprocess.check_call(['wget', '-O', os.path.join(dest_path, '{}.zip'.format(self.name)), self.url], stdout=build_log, stderr=err_log)
            except Exception as e:
                LOGGER.error('Cannot download release package for %s project', self.name)
                raise e
        LOGGER.info('Release package has been downloaded for %s project', self.name)
