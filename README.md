# platform-parent
Project for building all platform components

# Prerequisites

In order to build all platform components artifacts from Maven Central and from spring.io artifact repository are required. Below you can find example of settings.xml

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



# Steps to build:
 1. Make sure both maven central and repo.spring.io repositories locations are set in you settings.xml file
 1. clone project to local machine
 1. run git submodule update --init --recursive on platform-parent project
 1. run ./build-dependencies.sh

