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
import ConfigParser
import json

TARGET_CATALOG_NAME = 'PACKAGES'
YAML_FILE_PATH = 'projects_names.yml'
PLATFORM_PARENT_PATH = os.getcwd()

class Builder:
    def __init__(self, name):
        os.chdir(os.path.join(PLATFORM_PARENT_PATH, name))
        self.name = name
    def build(self):
        pass

    def get_zip_name(self):
        pass
  
    def _create_package_path(self, name, version):
        return "{}-{}".format(name, version), os.path.join(name, version)
   
class JavaBuilder(Builder):
    def __init__(self, name):
        Builder.__init__(self, name)

    def build(self):
        subprocess.check_call(['mvn', 'clean', 'install'])        

    def get_zip_name(self):
        version = ElementTree(file='pom.xml').findtext('{http://maven.apache.org/POM/4.0.0}version')
        name = self.name[:-1] if self.name[-1] == "/" else self.name

        if len(name.split('/')) == 1:
            version = ElementTree(file='pom.xml').findtext('{http://maven.apache.org/POM/4.0.0}version')
            pkg_name = name
        else:
            version = ElementTree(file='../pom.xml').findtext('{http://maven.apache.org/POM/4.0.0}version')
            pkg_name = name.split('/')[-1]

        return self._create_package_path(pkg_name, version)

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

    def get_zip_name(self):
        config = ConfigParser.ConfigParser()
        config.read('.bumpversion.cfg')
        version = config.get('bumpversion', 'current_version')
        return self._create_package_path(self.name, version)


class PythonBuilder(Builder):
    def __init__(self, name):
         Builder.__init__(self, name)
    
    def build(self):
        if not os.path.exists('vendor'):
            os.makedirs('vendor')
        subprocess.check_call(['pip', 'install', '--download', 'vendor', '-r', 'requirements.txt'])
        subprocess.check_call(['tox', '-r'])

    def get_zip_name(self):
        config = ConfigParser.ConfigParser()
        config.read('.bumpversion.cfg')
        version = config.get('bumpversion', 'current_version')
        return self._create_package_path(self.name, version)



class ConsoleBuilder(Builder):
    def __init__(self, name):
        Builder.__init__(self, name)

    def build(self):
        subprocess.check_call(['npm', 'install'])
        subprocess.check_call(['node', './node_modules/gulp/bin/gulp.js'])

    def get_zip_name(self):
        with open('package.json') as f:
            package_json = json.load(f)
        version = package_json['version']
        return self._create_package_path(self.name, version)


class WssbBuilder(GoBuilder):
    def __init__(self, name):
        GoBuilder.__init__(self, name)

    def get_zip_name(self):
        return "wssb", "."

def load_app_yaml(path):
    with open(path, 'r') as stream:
        return yaml.load(stream)

def create_zip_package(name, zip_name, path, items):
    print path
    
    if not os.path.exists(path):
        os.makedirs(path)
    if os.path.exists(os.path.join(path, zip_name + '.zip')):
        os.remove(os.path.join(path, zip_name + '.zip'))
        
    zip_package = zipfile.ZipFile(os.path.join(path, zip_name + '.zip'), 'w')
    os.chdir(os.path.join(PLATFORM_PARENT_PATH, name))

    for item in items:
        item = item.format(name=zip_name)
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
        skip_zip = project["skip_zip"] if "skip_zip" in project else False
        skip_build = project["skip_build"] if "skip_build" in project else False
        name = project['name']
        language = project['language']
        builder = builders[language](name)
        if not skip_build:
            builder.build()

        if not skip_zip:
            if items is not None:
                zip_name, rel_path = builder.get_zip_name()
                create_zip_package(name, zip_name, os.path.join(PLATFORM_PARENT_PATH, TARGET_CATALOG_NAME, rel_path), items)


def main():
    projects_names = load_app_yaml(YAML_FILE_PATH)
    build_projects(projects_names)

if __name__ == '__main__':
    main()

