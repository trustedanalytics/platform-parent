# platform-parent
Platform-parent is a tool for downloading sources and building all TAP applications.
After running this tool, deployable artifacts will be created. Next these artifacts can be used as an input for [apployer](https://github.com/trustedanalytics/apployer) tool, which is able to deploy them to the TAP environment.

# Prerequisites
 1. Follow [Development Environment Setup](https://github.com/trustedanalytics/platform-wiki-latest/wiki/Development-Environment-Setup) instructions.
 1. Install `pyyaml` package running command ```sudo pip install pyyaml```.
 1. In order to build all platform components artifacts from Maven Central and other external locations are required. On your dev machine [settings.xml](https://github.com/intel-data/platform-parent/blob/master/docker/settings.xml) should be stored in `~/.m2/` catalog (maven configuration files). If you already have your settings in `settings.xml` file, you should merge TAP `settings.xml` with yours.

# Steps to build:
 1. Clone platform-parent project to your local machine.
 1. Run script using ```python build_platform.py``` in platform-parent directory.

# Running options
  1. ```python build_platform -r / --refs-txt <path_to_refs_txt>``` Setting path for refs.txt file (specified versions of all projects).
  1. ```python build_platform -s / --spec-version <project_name>:<id>``` You can build specified version of project. As ID you can provide commit ID or branch/release name.
  1. ```python build_platform -d / --destination <path>``` Determines destination path.
  1. ```python build_platform -t / --release-tag <tag>``` Determines release tag for TAP repositories (-s argument has higher priority.
  1. ```python build_platform -a / --atk-version <version>``` Determines ATK components version.

For adding new TAP application to platform-parent `cloud_apps.yml` should be edited.

# Running platform-parent from docker container:
Latest version of Docker can be installed on Linux by following instructions provided here: https://docs.docker.com/linux/step_one/.

Steps to build docker image and run platform-parent tool from docker container:
  1. Enter ```platform-parent/docker``` directory.
  1. Run following command to create docker image: ```./build_tap.sh build```
  1. Create `ARTIFACTS_OUTPUT_PATH` catalog.
  1. Run docker container by executing: ```./build_tap.sh run PLATFORM_PARENT_PATH ARTIFACTS_OUTPUT_PATH <platform-parent-options>```. Artifacts will be stored in `/artifacts` directory on Docker container and in `ARTIFACTS_OUTPUT_PATH` directory on host machine.

  PLATFORM-PARENT-OPTIONS should be in OPTION=VALUE form, for example: --release-tag=v0.7
