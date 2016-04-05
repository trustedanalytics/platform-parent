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
import glob
import shutil
import threading
import argparse
import yaml
import subprocess
import builders.constants as constants

from Queue import Queue
from builders.java_builder import JavaBuilder
from builders.go_builder import GoBuilder
from builders.wssb_builder import WssbBuilder
from builders.tool_builder import ToolBuilder
from builders.universal_builder import UniversalBuilder
from builders.console_builder import ConsoleBuilder
from builders.gearpumpbroker_builder import GearpumpBrokerBuilder
from builders.atk_builder import AtkBuilder
from builders.release_downloader import ReleaseDownloader
from lib.logger import LOGGER

threads = []
LOCK = threading.Lock()

def build_sources():
    builders = {
        'go': GoBuilder,
        'wssb': WssbBuilder,
        'tool': ToolBuilder,
        'universal': UniversalBuilder,
        'java': JavaBuilder,
        'console': ConsoleBuilder,
        'gearpump': GearpumpBrokerBuilder,
        'atk': AtkBuilder,
        'release_downloader': ReleaseDownloader
    }
    while apps_queue.empty() is not True:
        app = apps_queue.get()
        builder = builders[app['builder']](app)
        if app['builder'] == 'release_downloader':
            builder.download_release_zip(apps_output_path)
        elif app['builder'] != 'atk':
            builder.download_project_sources(snapshot=release_tag, url=os.path.join(constants.TAP_REPOS_URL, app['name']))
            builder.build()
            destination_zip_path = tools_output_path if app['builder'] == 'tool' else apps_output_path
            if app['builder'] == 'universal':
                zip_path = glob.glob('{0}/{0}*.zip'.format(app['name']))[0]
                shutil.copy(zip_path, destination_zip_path)
            else:
                builder.create_zip_package(destination_zip_path)
            LOCK.acquire()
            refs_summary[builder.name] = builder.ref
            LOCK.release()
        else:
            builder.download_project_sources(snapshot=atk_version, url=constants.ATK_REPOS_URL)
            builder.build()
            builder.create_deployable_zip(apps_output_path, extra_files_paths=[os.path.join(constants.PLATFORM_PARENT_PATH, 'utils', app['name'], 'manifest.yml')])

def load_app_yaml(path):
    with open(path, 'r') as stream:
        return yaml.load(stream)

def run_apployer_expand():
    apployer_repo_path = os.path.join(constants.PLATFORM_PARENT_PATH, 'apployer')
    subprocess.check_call(['tox', '-r'], cwd=apployer_repo_path)
    subprocess.check_call([os.path.join('.tox', 'py27', 'bin', 'apployer'),
                           'expand', constants.PLATFORM_PARENT_PATH], cwd=apployer_repo_path)
    subprocess.check_call(['mv', os.path.join(apployer_repo_path, 'expanded_appstack.yml'), files_output_path], cwd=constants.PLATFORM_PARENT_PATH)

apps_queue = Queue()

def parse_args():
    parser = argparse.ArgumentParser(description="Downloads and builds TAP projects in specified version.")

    parser.add_argument('-r', '--refs-txt', required=False, help='Path to refs.txt file')
    parser.add_argument('-s', '--spec-version', nargs='+', required=False, help='Commit ID or branch with specified version'
                                                                     'of project. Usage: -s <project_name> <version>')
    parser.add_argument('-d', '--destination', required=False, help='Destination path for zip packages.')
    parser.add_argument('-t', '--release-tag', required=False, help='Specifies a release tag for TAP repositories.')
    parser.add_argument('-a', '--atk-version', required=False, help='Specifies a ATK components version.')

    return parser.parse_args()

def main():
    global tools_output_path, apps_output_path, files_output_path, release_tag, atk_version, destination_path, refs_summary
    refs_summary = dict()

    args = parse_args()

    input_refs_file = dict()
    if args.refs_txt:
        try:
            with open(args.refs_txt, 'r') as stream:
                refs_txt_content = stream.read().split('\n')
            for item in refs_txt_content:
                item = item.split()
                if len(item):
                    input_refs_file[item[0]] = item[1]
        except Exception:
            LOGGER.error('Cannot open refs.txt file.')

    if args.spec_version:
        for ver in args.spec_version:
            item = ver.split(':')
            input_refs_file[item[0]] = item[1]

    projects_names = load_app_yaml(constants.APPS_YAML_FILE_PATH)
    for app in projects_names['applications']:
        if 'snapshot' not in app:
            app['snapshot'] = input_refs_file[app['name']] if app['name'] in input_refs_file else None
        apps_queue.put(app)

    destination_path = args.destination if args.destination else constants.DEFAULT_DESTINATION_PATH
    tools_output_path = os.path.join(destination_path, 'tools')
    apps_output_path = os.path.join(destination_path, 'apps')
    files_output_path = os.path.join(destination_path, 'files')

    release_tag = args.release_tag if args.release_tag else None
    atk_version = args.atk_version if args.atk_version else constants.DEFAULT_ATK_VERSION

    if not os.path.exists(tools_output_path):
        os.makedirs(tools_output_path)
    if not os.path.exists(apps_output_path):
        os.makedirs(apps_output_path)
    if not os.path.exists(files_output_path):
        os.makedirs(files_output_path)

    for i in range(constants.CPU_CORES_COUNT):
        threads.append(threading.Thread(target=build_sources))
        threads[i].start()

    for i in range(constants.CPU_CORES_COUNT):
        threads[i].join()

    with open(os.path.join(files_output_path, 'refs.txt'), 'w') as ref_file:
        for key, value in refs_summary.iteritems():
            ref_file.write('{} {}\n'.format(key, value))

    run_apployer_expand()


if __name__ == '__main__':
    main()

