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
import multiprocessing
import threading

from Queue import Queue
from builders.java_builder import JavaBuilder
from builders.go_builder import GoBuilder
from builders.wssb_builder import WssbBuilder
from builders.tool_builder import ToolBuilder
from builders.python_builder import PythonBuilder
from builders.console_builder import ConsoleBuilder
from builders.gearpumpbroker_builder import GearpumpBrokerBuilder
from builders.atk_builder import AtkBuilder
from builders.constants import *

# Reading number of processors due to creating threads per processor which runs subprocess commands
CPU_CORES_COUNT = multiprocessing.cpu_count()

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
    projects_names = load_app_yaml(APPS_YAML_FILE_PATH)
    for app in projects_names['applications']:
        apps_queue.put(app)

    for i in range(CPU_CORES_COUNT):
        t = threading.Thread(target=build_sources)
        t.start()

if __name__ == '__main__':
    main()

