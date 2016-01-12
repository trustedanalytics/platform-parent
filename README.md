# platform-parent
Project for building all platform components.

# Steps to build:

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
 1. Make sure both maven central and repo.spring.io repositories locations are set in you settings.xml file.
 1. Before next step make sure that you installed all required components mentioned on the [Development Environment Setup](https://github.com/trustedanalytics/platform-wiki/wiki/Development-Environment-Setup) page.
 1. Clone platform-parent project to your local machine.
 1. Fill custom variables in build-dependencies.py file.
 1. Install pyyaml running command ```sudo pip install pyyaml```.
 1. Run script using  ```python build_dependencies.py``` in platform-parent directory.


The artifacts will be stored in directory specified in custom variables. If you are using [cloudfoundry-mkappstack](https://github.com/trustedanalytics/cloudfoundry-mkappstack) to deploy platform, the path to the artifacts must be set. In order to do this, set the following values to ```artifact_pfx``` and ```afcturl``` fields in appstack.mk file:

```
artifact_pfx = file:///tmp/PACKAGES
afcturl = $(artifact_pfx)/$(appname).zip
```
