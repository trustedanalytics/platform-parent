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

import subprocess
import os

from builders.builder import Builder
from lib.logger import LOGGER
from builders.constants import PLATFORM_PARENT_PATH

class GoBuilder(Builder):

    def __init__(self, app_info):
        Builder.__init__(self, app_info)

    def build(self):
        LOGGER.info('Building {} project using godep'.format(self.name))
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            try:
                subprocess.check_call(['godep', 'go', 'build', './...'],
                                      cwd=self.sources_path, stdout=build_log, stderr=err_log)
            except Exception as e:
                LOGGER.error('Cannot build {} project using godep'.format(self.name))
                raise e
        LOGGER.info('Building {} project using godep has been finished'.format(self.name))

    def download_project_sources(self, snapshot=None, url=None):
        Builder.download_project_sources(self, snapshot, url)
        godep_path = os.path.join(os.environ["GOPATH"], 'src/github.com/trustedanalytics/')
        if not os.path.exists(godep_path):
            os.makedirs(godep_path)
        if not os.path.exists(os.path.join(godep_path, self.name)):
            os.symlink(os.path.join(PLATFORM_PARENT_PATH, self.name), os.path.join(godep_path, self.name))