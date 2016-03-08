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

import yaml
import subprocess
import os
import json
import zipfile
from xml.etree.ElementTree import ElementTree
import requests
import tarfile
import shutil
import ntpath
import multiprocessing
import threading
from Queue import Queue
import logging

################# CUSTOM VARIABLES #####################
# configuration file path with list of applications
YAML_FILE_PATH = 'cloud_apps.yml'

# path for zip packages storing
DESTINATION_ABS_PATH = '/tmp'
TARGET_CATALOG_NAME = 'PACKAGES'

# project sources configuration
TAP_REPOS_URL = 'https://github.com/trustedanalytics/'
RELEASE_TAG = None
ATK_REPOS_URL = 'https://analytics-tool-kit.s3-us-west-2.amazonaws.com/public/weekly/regressed/'
ATK_VERSION = 'latest'
########################################################

PLATFORM_PARENT_PATH = os.getcwd()
GEARPUMP_BINARIES_URL = 'https://github.com/gearpump/gearpump/releases/download/{short_ver}/gearpump-{long_ver}.zip'

# Reading number of processors due to creating threads per processor which runs subprocess commands
CPU_CORES_COUNT = multiprocessing.cpu_count()

def set_up_logger(name):
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    ch = logging.StreamHandler()
    ch.setLevel(level=logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    return logger

LOGGER = set_up_logger('BUILDER')

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
        LOGGER.info('Package {} for {} project has been created'.format(zip_name, self.name))


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
        LOGGER.info('Package {} for {} project has been created'.format(zip_name, self.name))


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


class PythonBuilder(Builder):
    def build(self):
        LOGGER.info('Building {} project'.format(self.name))
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            try:
                subprocess.check_call(['sh', 'cf_build.sh'],
                                      cwd=self.sources_path, stdout=build_log, stderr=err_log)
            except Exception as e:
                LOGGER.error('Cannot build {} project'.format(self.name))
                raise e
        LOGGER.info('Building {} project has been finished'.format(self.name))


class ConsoleBuilder(Builder):
    def build(self):
        LOGGER.info('Building {} project'.format(self.name))
        with open(self.build_log_path, 'a') as build_log, \
                open(self.err_log_path, 'a') as err_log:
            try:
                subprocess.check_call(['npm', 'install'], cwd=self.sources_path, stdout=build_log, stderr=err_log)
                subprocess.check_call(['node', './node_modules/gulp/bin/gulp.js', 'build'],
                                      cwd=self.sources_path, stdout=build_log, stderr=err_log)
                subprocess.check_call(['rm', '-rf', 'node_modules', 'bower_components', '.cfignore'],
                                      cwd=self.sources_path, stdout=build_log, stderr=err_log)
                subprocess.check_call(['npm', 'install', '--production'],
                                      cwd=self.sources_path, stdout=build_log, stderr=err_log)
            except Exception as e:
                LOGGER.error('Cannot build {} project'.format(self.name))
                raise e
        LOGGER.info('Building {} project has been finished'.format(self.name))


class WssbBuilder(GoBuilder):
    def __init__(self, name):
        GoBuilder.__init__(self, name)

class AtkBuilder(Builder):

    LATEST_VERSION = 'latest'

    def __init__(self, app_info):
        self.name = app_info['name']
        self.tar_name = app_info['tar_name']
        self.zip_name = app_info['zip_name'] if 'zip_name' in app_info else None
        self.save_versions_catalog()

    def save_versions_catalog(self):
        versions_url = os.path.join(ATK_REPOS_URL, 'version.json')
        try:
            response = requests.get(versions_url)
        except requests.exceptions.RequestException as e:
            LOGGER.error('Cannot building {} project. Cannot get versions catalog.'.format(self.name))
            raise e
        self._versions_catalog = json.loads(response.text)

    def download_project_sources(self, snapshot=None, url=None):
        self.url = url
        self.download_tar_file(self.tar_name, snapshot, os.path.join(PLATFORM_PARENT_PATH, '{}.tar.gz'.format(self.name)))

    def download_tar_file(self, tar_name, version, dest_tar_path):
        LOGGER.info('Downloading {} in version for {} project'.format(tar_name, version, self.name))
        self._local_tar_path = dest_tar_path
        if version.lower() == self.LATEST_VERSION:
            self._version_in_manifest = self._versions_catalog[self.LATEST_VERSION]['release']
            catalog_name_in_path = self.LATEST_VERSION
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
        return self.LATEST_VERSION


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


class ToolBuilder(Builder):
    def __init__(self, app_info):
        Builder.__init__(self, app_info)


def build_sources():
    builders = {
        'go': GoBuilder,
        'wssb': WssbBuilder,
        'tool': ToolBuilder,
        'python': PythonBuilder,
        'java': JavaBuilder,
        'console': ConsoleBuilder,
        'gearpump': GearpumpBrokerBuilder,
        'atk': AtkBuilder
    }
    while apps_queue.empty() is not True:
        app = apps_queue.get()
        builder = builders[app['builder']](app)
        if app['builder'] != 'atk':
            builder.download_project_sources(snapshot=RELEASE_TAG, url=os.path.join(TAP_REPOS_URL, app['name']))
            builder.build()
            destination_zip_path = os.path.join(DESTINATION_ABS_PATH, TARGET_CATALOG_NAME, 'tools') if app['builder'] == 'tool' \
                else os.path.join(DESTINATION_ABS_PATH, TARGET_CATALOG_NAME, 'apps')
            builder.create_zip_package(destination_zip_path)
        else:
            builder.download_project_sources(snapshot=ATK_VERSION, url=ATK_REPOS_URL)
            builder.build()
            builder.create_deployable_zip(os.path.join(DESTINATION_ABS_PATH, TARGET_CATALOG_NAME, 'apps'),
                                          extra_files_paths=[os.path.join(PLATFORM_PARENT_PATH, 'utils', app['name'], 'manifest.yml')])

def load_app_yaml(path):
    with open(path, 'r') as stream:
        return yaml.load(stream)

apps_queue = Queue()

def main():
    projects_names = load_app_yaml(YAML_FILE_PATH)
    for app in projects_names['applications']:
        apps_queue.put(app)

    for i in range(CPU_CORES_COUNT):
        t = threading.Thread(target=build_sources)
        t.start()

if __name__ == '__main__':
    main()

