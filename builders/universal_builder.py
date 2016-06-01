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

from builders.builder import Builder
from lib.logger import LOGGER

class UniversalBuilder(Builder):

    def build(self):
        LOGGER.info('Building %s project', self.name)
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            try:
                subprocess.check_call(['sh', 'pack.sh'], cwd=self.sources_path,
                                      stdout=build_log, stderr=err_log)
            except Exception as e:
                LOGGER.error('Cannot build {} project'.format(self.name))
                raise e
        LOGGER.info('Building {} project has been finished'.format(self.name))
