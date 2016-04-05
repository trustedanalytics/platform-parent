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
import requests
import json
import ntpath
import tarfile
import shutil
import zipfile
import yaml

from builders.builder import Builder
from lib.logger import LOGGER
from builders.constants import ATK_REPOS_URL
from builders.constants import PLATFORM_PARENT_PATH
from builders.constants import LATEST_ATK_VERSION

class AtkBuilder(Builder):

    def __init__(self, app_info):
        self.name = app_info.get('name')
        self.tar_name = app_info.get('tar_name')
        self.zip_name = app_info.get('zip_name')
        self._save_versions_catalog()

    def _save_versions_catalog(self):
        versions_url = os.path.join(ATK_REPOS_URL, 'version.json')
        try:
            response = requests.get(versions_url)
        except requests.exceptions.RequestException as e:
            LOGGER.error('Cannot building {} project. Cannot get versions catalog.'.format(self.name))
            raise e
        self._versions_catalog = json.loads(response.text)

    def download_project_sources(self, snapshot=None, url=None):
        self.url = url
        self._download_tar_file(self.tar_name, snapshot, os.path.join(PLATFORM_PARENT_PATH, '{}.tar.gz'.format(self.name)))

    def _download_tar_file(self, tar_name, version, dest_tar_path):
        LOGGER.info('Downloading {} in version {} for {} project'.format(tar_name, version, self.name))
        self._local_tar_path = dest_tar_path
        if version.lower() == LATEST_ATK_VERSION:
            self._version_in_manifest = self._versions_catalog[LATEST_ATK_VERSION]['release']
            catalog_name_in_path = LATEST_ATK_VERSION
        else:
            self._version_in_manifest = version
            catalog_name_in_path = self._get_catalog_name_by_release_number(version)
        download_url = os.path.join(self.url, catalog_name_in_path, 'binaries', tar_name)

        try:
            response = requests.get(download_url)
            with open(dest_tar_path, 'wb') as tar:
                tar.write(response.content)
        except requests.exceptions.RequestException as e:
            LOGGER.error('Cannot download {} tar archive for {} project.'.format(tar_name, self.name))
            raise e
        except IOError as e:
            LOGGER.error('Cannot save {} tar archive on your hard disk.'.format(tar_name))
            raise e

        LOGGER.info('Tar archive for {} app from {} in version {} has been downloaded'
                    .format(self.name, download_url, version))

    def build(self):
        self.extract_tar_file(os.path.join(PLATFORM_PARENT_PATH, self.name))

    def extract_tar_file(self, dest_path, source_path=None):
        tar_path = source_path if source_path else self._local_tar_path
        self._local_sources_path = dest_path
        try:
            tar = tarfile.open(tar_path)
            tar.extractall(self._local_sources_path)
            tar.close()
        except Exception as e:
            LOGGER.error('Cannot extract tar file for {} project'.format(self.name))
            raise e

    def create_deployable_zip(self, path_for_zip, sources_path=None, extra_files_paths=None):
        LOGGER.info('Creating zip package for {} project'.format(self.name))
        if not os.path.exists(path_for_zip):
            os.makedirs(path_for_zip)
        project_files_path = sources_path if sources_path else self._local_sources_path
        try:
            for extra_file_path in extra_files_paths:
                shutil.copyfile(extra_file_path, os.path.join(project_files_path, ntpath.basename(extra_file_path)))
                if ntpath.basename(extra_file_path) == 'manifest.yml':
                    app_manifest_path = os.path.join(project_files_path, ntpath.basename(extra_file_path))
                    with open(app_manifest_path, 'r') as f_stream:
                        manifest_yml = yaml.load(f_stream)
                    manifest_yml['applications'][0]['env']['VERSION'] = self._version_in_manifest
                    with open(app_manifest_path, 'w') as f_stream:
                        f_stream.write(yaml.safe_dump(manifest_yml))
        except Exception as e:
            LOGGER.error('Cannot add extra files to {} project zip package'.format(self.name))
            raise e

        path_for_zip = os.path.join(path_for_zip, self.zip_name + '.zip') if self.zip_name else os.path.join(path_for_zip, self.name + '.zip')

        try:
            deployable_zip = zipfile.ZipFile(path_for_zip, 'w')
            for root, dirs, files in os.walk(project_files_path):
                for file in files:
                    deployable_zip.write(os.path.join(os.path.relpath(root, PLATFORM_PARENT_PATH), file),
                                         os.path.join(os.path.relpath(root, os.path.join(PLATFORM_PARENT_PATH, self.name)), file))
            deployable_zip.close()
        except Exception as e:
            LOGGER.error('Cannot create zip package for {}'.format(self.name))
            raise e

        LOGGER.info("Package for {} has been created".format(self.name))

    def _get_catalog_name_by_release_number(self, release_number):
        for key, value in self._versions_catalog.iteritems():
            if value['release'] == int(release_number):
                return key
        LOGGER.warning('Unknown release number for {} project. Latest version will be used.'.format(self.name))
        return LATEST_ATK_VERSION