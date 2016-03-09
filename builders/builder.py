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
import zipfile

from constants import PLATFORM_PARENT_PATH
from lib.logger import LOGGER

class Builder:

    def __init__(self, app_info):
        self.name = app_info['name']
        self.snapshot = app_info['snapshot'] if 'snapshot' in app_info else None
        self.url = app_info['url'] if 'url' in app_info else None
        self.sources_path = os.path.join(PLATFORM_PARENT_PATH, self.name)
        self.zip_name = app_info['zip_name'] + '.zip' if 'zip_name' in app_info else self.name + '.zip'
        self.zip_items = app_info['items'] if 'items' in app_info else [self.sources_path]
        self.logs_directory_path = os.path.join(PLATFORM_PARENT_PATH, 'logs')
        if not os.path.exists(self.logs_directory_path):
            os.makedirs(self.logs_directory_path)
        self.build_log_path = os.path.join(self.logs_directory_path, self.name + '-build.log')
        self.err_log_path = os.path.join(self.logs_directory_path, self.name + '-err.log')

    def build(self):
        pass

    def download_project_sources(self, snapshot=None, url=None):
        self.snapshot = self.snapshot if self.snapshot else snapshot
        self.url = self.url if self.url else url
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            if os.path.exists(self.sources_path):
                LOGGER.info('Updating sources for {} project'.format(self.name))
                try:
                    subprocess.check_call(['git', 'checkout', 'master'], cwd=self.sources_path, stdout=build_log, stderr=err_log)
                    subprocess.check_call(['git', 'pull'], cwd=self.sources_path, stdout=build_log, stderr=err_log)
                except Exception as e:
                    LOGGER.error('Cannot update sources for {} project'.format(self.name))
                    raise e
                LOGGER.info('Sources for {} project has been updated'.format(self.name))
            else:
                LOGGER.info('Downloading {} project sources'.format(self.name))
                try:
                    subprocess.check_call(['git', 'clone', self.url], cwd=PLATFORM_PARENT_PATH, stdout=build_log, stderr=err_log)
                except Exception as e:
                    LOGGER.error('Cannot download sources for {} project'.format(self.name))
                    raise e
                LOGGER.info('Sources for {} project has been downloaded'.format(self.name))
            if self.snapshot:
                LOGGER.info('Setting release tag {} for {} project sources'.format(self.snapshot, self.name))
                try:
                    subprocess.check_call(['git', 'checkout', self.snapshot], cwd=self.sources_path, stdout=build_log, stderr=err_log)
                except Exception:
                    LOGGER.warning('Cannot set release tag {} for {} project sources. Using "master" branch.'.format(self.snapshot, self.name))

    def create_zip_package(self, dest_path, zip_name=None, zip_items=None):
        zip_name = zip_name if zip_name else self.zip_name
        LOGGER.info('Creating {} package for {} project'.format(zip_name, self.name))
        try:
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            if os.path.exists(os.path.join(dest_path, zip_name)):
                os.remove(os.path.join(dest_path, zip_name))
            zip_package = zipfile.ZipFile(os.path.join(dest_path, zip_name), 'w')

            zip_items = zip_items if zip_items else self.zip_items
            if zip_items:
                zip_items_abs_paths = []
                for item in zip_items:
                    zip_items_abs_paths.append(os.path.join(self.sources_path, item))

            for item in zip_items_abs_paths:
                if os.path.isdir(item):
                    for root, dirs, files in os.walk(item):
                        for file in files:
                            zip_package.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), self.sources_path))
                else:
                    zip_package.write(item, os.path.relpath(item, self.sources_path))
            zip_package.close()
        except Exception as e:
            LOGGER.error('Cannot create zip package {} for {} project'.format(zip_name, self.name))
            raise e
        LOGGER.info('Package for {} project has been created'.format(self.name))