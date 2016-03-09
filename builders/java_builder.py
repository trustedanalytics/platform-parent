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

from xml.etree.ElementTree import ElementTree
from builders.builder import Builder
from lib.logger import LOGGER

class JavaBuilder(Builder):

    def __init__(self, app_info):
        Builder.__init__(self, app_info)

    def build(self):
        LOGGER.info('Building {} project using maven'.format(self.name))
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            try:
                subprocess.check_call(['mvn', 'clean', 'install', '-Dmaven.test.skip=true'],
                                      cwd=self.sources_path, stdout=build_log, stderr=err_log)
            except Exception as e:
                LOGGER.error('Cannot build {} project using maven'.format(self.name))
                raise e
        LOGGER.info('Building {} project using maven has been finished'.format(self.name))

    def create_zip_package(self, dest_path, zip_name=None, zip_items=None):
        LOGGER.info('Creating {} package for {} project'.format(zip_name, self.name))
        try:
            self.version = ElementTree(file=os.path.join(self.sources_path, 'pom.xml')).findtext('{http://maven.apache.org/POM/4.0.0}version')
        except Exception as e:
            LOGGER.error('Cannot retrieve project version for {} project'.format(self.name))
            raise e
        self.zip_items = zip_items if zip_items else ['manifest.yml', 'target/{}-{}.jar'.format(self.name, self.version)]
        Builder.create_zip_package(self, dest_path, zip_name=zip_name, zip_items=zip_items)
        LOGGER.info('Package for {} project has been created'.format(self.name))