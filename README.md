# platform-parent
Project for building all platform components.

# Steps to build:

 1. Make sure that repositories locations from the config file are set in you settings.xml file.
 1. Before next step make sure that you installed all required components mentioned on the [Development Environment Setup](https://github.com/trustedanalytics/platform-wiki/wiki/Development-Environment-Setup) page.
 1. Clone platform-parent project to your local machine.
 1. Install pyyaml running command ```sudo pip install pyyaml```.
 1. Run script using ```python build_platform.py``` in platform-parent directory.

In order to build all platform components artifacts from Maven Central and from spring.io artifact repository are required. Below you can find example of settings.xml. You should copy it to your settings.xml file, which is included in ~/.m2/ catalog. Maven stores configuration files at this place. 

If you already have your settings in settings.xml file, you should join profile from example below to your setting.xml file and set this profile as active.

```
<?xml version="1.0" encoding="UTF-8"?>
<settings xsi:schemaLocation="http://maven.apache.org/SETTINGS/1.1.0 http://maven.apache.org/xsd/settings-1.1.0.xsd" xmlns="http://maven.apache.org/SETTINGS/1.1.0"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <profiles>
    <profile>
      <repositories>
        <repository>
          <id>Maven Central</id>
          <url>http://repo1.maven.org/maven2/</url>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
        </repository> 
        <repository>
          <id>cloudera</id>
          <url>https://repository.cloudera.com/artifactory/cloudera-repos/</url>
        </repository>
        <repository>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
          <id>central</id>
          <name>libs-release-remote</name>
          <url>http://repo.spring.io/libs-release-remote</url>
        </repository>
        <repository>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
          <id>local central</id>
          <name>libs-release-local</name>
          <url>http://repo.spring.io/libs-release-local</url>
        </repository>
        <repository>
          <snapshots />
          <id>snapshots</id>
          <name>libs-snapshot-remote</name>
          <url>http://repo.spring.io/libs-snapshot-remote</url>
        </repository>
      </repositories>
      <pluginRepositories>
        <pluginRepository>
          <snapshots>
            <enabled>false</enabled>
          </snapshots>
          <id>central</id>
          <name>plugins-release</name>
          <url>http://repo.spring.io/plugins-release</url>
        </pluginRepository>
        <pluginRepository>
          <snapshots />
          <id>snapshots</id>
          <name>plugins-snapshot</name>
          <url>http://repo.spring.io/plugins-snapshot</url>
        </pluginRepository>
      </pluginRepositories>
      <id>artifactory</id>
    </profile>
  </profiles>
  <activeProfiles>
    <activeProfile>artifactory</activeProfile>
  </activeProfiles>
</settings>
```

The artifacts will be stored in directory specified in custom variables. If you are using [cloudfoundry-mkappstack](https://github.com/trustedanalytics/cloudfoundry-mkappstack) to deploy platform, the path to the artifacts must be set. In order to do this, set the following values to ```artifact_pfx``` and ```afcturl``` fields in appstack.mk file:

```
artifact_pfx = file:///tmp/PACKAGES
afcturl = $(artifact_pfx)/$(appname).zip
```

# Tips
  1. ```python build_platform -r <path_to_refs_txt>``` Setting path for refs.txt file (specified versions of all projects).
  1. ```python build_platform -s <project_name>:<id>``` You can build specified version of project. As ID you can provide commit ID or branch/release name.
  1. ```python build_platform -d <path>``` Determines destination path.
  1. ```python build_platform -t <tag>``` Determines release tag for TAP repositories (-s argument has higher priority.
  1. ```python build_platform -a <version>``` Determines ATK components version.

# Building from docker container:

Latest version of Docker can be installed on Linux by following instructions provided here: https://docs.docker.com/linux/step_one/.

Steps to build:
  1. Enter ```platform-parent/docker``` directory.
  1. Run following command to create docker image: ```docker build -t platform-parent .```
     (if you are behind proxy, run ```docker build --build-arg http_proxy='your_http_proxy' --build-arg https_proxy='your_https_proxy' -t platform-parent . ```).
  1. Run docker container by executing: ```docker run -i -t platform-parent```.
     (if you are behind proxy, run ```docker run -i -t -e http_proxy='your_http_proxy' -e https_proxy='your_https_proxy' platform-parent ```).
  1. Enter ```/root/platform-parent``` directory and run ```python build-dependencies.py```
     (if you are behind proxy, configure proxy settings in ```/usr/share/maven/conf/settings.xml``` file before running build-dependencies.py script, see https://maven.apache.org/guides/mini/guide-proxies.html for reference).
