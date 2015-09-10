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
import zipfile
from xml.etree.ElementTree import ElementTree

TARGET_CATALOG_NAME = 'PACKAGES'
YAML_FILE_PATH = 'cloud_apps.yml'
PLATFORM_PARENT_PATH = os.getcwd()
DESTINATION_PATH = '/tmp'


class Builder:
    def __init__(self, name):
        os.chdir(os.path.join(PLATFORM_PARENT_PATH, name))
        self.name = name

    def build(self):
        pass


class JavaBuilder(Builder):
    def __init__(self, name):
        Builder.__init__(self, name)

    def build(self):
        subprocess.check_call(['mvn', 'clean', 'install', '-U'])


class GoBuilder(Builder):        
    def __init__(self, name):
        godep_path = os.path.join(os.environ["GOPATH"], 'src/github.com/trustedanalytics/')
        if not os.path.exists(godep_path):
            os.makedirs(godep_path)
        if not os.path.exists(os.path.join(godep_path, name)):
            os.symlink(os.path.join(PLATFORM_PARENT_PATH, name), os.path.join(godep_path, name))
        os.chdir(os.path.join(PLATFORM_PARENT_PATH, name))
        self.name = name

    def build(self):
        subprocess.check_call(['godep', 'go', 'build', './...'])
        subprocess.check_call(['godep', 'go', 'test', './...'])


class PythonBuilder(Builder):
    def __init__(self, name):
        Builder.__init__(self, name)
    
    def build(self):
        if not os.path.exists('vendor'):
            os.makedirs('vendor')
        subprocess.check_call(['pip', 'install', '--download', 'vendor', '-r', 'requirements.txt'])
        subprocess.check_call(['tox', '-r'])


class ConsoleBuilder(Builder):
    def __init__(self, name):
        Builder.__init__(self, name)

    def build(self):
        subprocess.check_call(['npm', 'install'])
        subprocess.check_call(['node', './node_modules/gulp/bin/gulp.js'])


class WssbBuilder(GoBuilder):
    def __init__(self, name):
        GoBuilder.__init__(self, name)

def load_app_yaml(path):
    with open(path, 'r') as stream:
        return yaml.load(stream)

def create_zip_package(zip_name, path, items):
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.exists(os.path.join(path, zip_name + '.zip')):
        os.remove(os.path.join(path, zip_name + '.zip'))
        
    zip_package = zipfile.ZipFile(os.path.join(path, zip_name + '.zip'), 'w')
    os.chdir(os.path.join(PLATFORM_PARENT_PATH, zip_name))

    for item in items:
        if 'jar' in item:
            version = ElementTree(file='pom.xml').findtext('{http://maven.apache.org/POM/4.0.0}version')
            jar_name = "{}-{}".format(zip_name, version)
            item = item.format(name=jar_name)
        if os.path.isdir(item):
            for root, dirs, files in os.walk(item):
                for file in files:
                    zip_package.write(os.path.join(root, file))
        else:
            zip_package.write(item)

    zip_package.close()
    os.chdir(PLATFORM_PARENT_PATH)


def build_projects(project_names):
    builders = {
        'java': JavaBuilder,
        'go': GoBuilder,
        'python': PythonBuilder,
        'console': ConsoleBuilder,
        'wssb' : WssbBuilder
    }

    for project in project_names['applications']:
        items = project["items"] if 'items' in project else None
        name = project['name']
        language = project['language']
        builder = builders[language](name)
        builder.build()

        if items is not None:
            create_zip_package(name, os.path.join(DESTINATION_PATH, TARGET_CATALOG_NAME), items)


def main():
    projects_names = load_app_yaml(YAML_FILE_PATH)
    build_projects(projects_names)

if __name__ == '__main__':
    main()

