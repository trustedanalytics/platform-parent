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
import subprocess
import shutil
import zipfile

from builders.java_builder import JavaBuilder
from builders.builder import Builder
from builders.constants import GEARPUMP_BINARIES_URL
from builders.constants import PLATFORM_PARENT_PATH
from builders.constants import DESTINATION_ABS_PATH
from builders.constants import TARGET_CATALOG_NAME
from lib.logger import LOGGER

class GearpumpBrokerBuilder(JavaBuilder):

    def __init__(self, app_info):
        Builder.__init__(self, app_info)

    def build(self):
        self.download_gearpump_binaries(os.path.join(PLATFORM_PARENT_PATH, self.name, 'src/main/resources/gearpump'))
        JavaBuilder.build(self)

    def download_gearpump_binaries(self, dest_path):
        try:
            with open(os.path.join(PLATFORM_PARENT_PATH, self.name, 'src', 'cloudfoundry', 'manifest.yml'), 'r') as stream:
                gearpump_broker_manifest = yaml.load(stream)
        except Exception as e:
            LOGGER.error('Cannot load manifest file for {} project'.format(self.name))
            raise e

        full_gearpump_binary_version = gearpump_broker_manifest['applications'][0]['env']['GEARPUMP_PACK_VERSION']
        short_gearpump_version = full_gearpump_binary_version.split('-')[1]
        self.package_name = 'gearpump-{}'.format(full_gearpump_binary_version)
        self.gearpump_binaries_path = os.path.join(dest_path, 'gearpump-{}.zip'.format(full_gearpump_binary_version))
        LOGGER.info('Downloading gearpump binaries in version {}'.format(full_gearpump_binary_version))
        url = GEARPUMP_BINARIES_URL.format(short_ver=short_gearpump_version, long_ver=full_gearpump_binary_version)
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            try:
                subprocess.check_call(['wget', url, '-P', dest_path], stdout=build_log, stderr=err_log)
            except Exception as e:
                LOGGER.error('Cannot download gearpump binaries for {} project'.format(self.name))
                raise e
        LOGGER.info('Gearpump binaries in version {} has been downloaded for {} project'.format(full_gearpump_binary_version, self.name))

    def build_gearpump_dashboard(self):
        LOGGER.info('Building gearpump-dashboard')
        gearpump_tmp_data = os.path.join('/tmp', self.package_name)
        gearpump_dashboard_artifact_path = os.path.join(DESTINATION_ABS_PATH, TARGET_CATALOG_NAME, 'apps', 'gearpump-dashboard.zip')
        if os.path.exists(gearpump_dashboard_artifact_path):
            os.remove(gearpump_dashboard_artifact_path)
        try:
            with zipfile.ZipFile(self.gearpump_binaries_path) as gb:
                gb.extractall('/tmp')
        except Exception as e:
            LOGGER.error('Cannot extract gearpump binaries')

        try:
            with open(self.build_log_path, 'a') as build_log, \
                    open(self.err_log_path, 'a') as err_log:
                subprocess.check_call(['./prepare.sh', gearpump_tmp_data, gearpump_tmp_data],
                                      cwd=os.path.join(PLATFORM_PARENT_PATH, self.name, 'scripts'), stdout=build_log, stderr=err_log)
                subprocess.check_call(['zip', 'gearpump-dashboard.zip', 'manifest.yml', 'target/gearpump-dashboard.zip'],
                                      cwd=gearpump_tmp_data, stdout=build_log, stderr=err_log)
            shutil.move(os.path.join(gearpump_tmp_data, 'gearpump-dashboard.zip'),
                        os.path.join(DESTINATION_ABS_PATH, TARGET_CATALOG_NAME, 'apps'))
            shutil.rmtree(gearpump_tmp_data)
        except Exception as e:
            LOGGER.error('Error in gearpump dashboard building')
            raise e
        LOGGER.info('Gearpump-dashboard package has been created')

    def create_zip_package(self, dest_path, zip_name=None, zip_items=None):
        JavaBuilder.create_zip_package(self, dest_path, zip_name=zip_name, zip_items=zip_items)
        self.build_gearpump_dashboard()