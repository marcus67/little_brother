![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)
![CentOS-Logo](doc/centos-logo.png)
![OpenSuSe-Logo](doc/opensuse-logo.png)
![ArchLinux-Logo](doc/arch-linux-logo.jpeg)
![Alpine-Logo](doc/alpine-linux-logo.png)

# Installation on Non-Debian Distributions

If you don't have a Debian distribution running or at least a distribution using the Debian package format you
still may be able to install `LittleBrother` manually.

This page will outline how to do this.

## Prerequisites

Install the following Linux packages. Note that the exact names may differ in your distribution.

| Debian Package           | CentOS Package            | Arch Linux Package   | Alpine package        |
|--------------------------|-------------------------- |----------------------|-----------------------|
|   preinstalled           | preinstalled              | preinstalled         | `bash`                |
|   `python3`              | `python3`                 | `python3`            | `python3`             |
|   `python3-pip`          | `python3-pip`             | `python-pip`         | `py3-pip`             |
|   `python3-dev`          | `python3-devel`           | not required         | `python3-devel`       |
|   `sudo`                 | `sudo`                    | `sudo`               | `sudo`                |
|   `procps` (master only) | `procps-ng` (master only) | TODO                 | TODO                  |
|   `virtualenv`           | `python3-virtualenv`      | `python-virtualenv`  | `py3-virtualenv`      |
|   `libsasl2-dev`         | TODO                      | not required         | `libsasl`             |
|   not required           | TODO                      | not required         | `libldap=2.5.58`      |
|   not required           | TODO                      | not required         | `libldapcpp=2.5.58`   |
|   `libldap2-dev`         | TODO                      | not required         | `openldap-dev=2.5.58` |
|   not required           | TODO                      | not required         | `libffi-dev`          |
|   `libssl-dev`           | TODO                      | not required         | not required          |
|   not required           | TODO                      | `curl`               | `curl`                |
|   not required           | TODO                      | `gcc`                | `gcc`                 |

## Installation Steps

* Download the current GitHub project as a 
  [master branch zipped tar file](https://github.com/marcus67/little_brother/archive/master.zip) or
  [release branch zipped tar file](https://github.com/marcus67/little_brother/archive/release.zip) 
 and store it locally.
    
* Unzip the archive by executing `unzip master.zip`.

* The base directory of the unzipped archive containing the `README.md` will be referenced as `$INSTALL_BASE_DIR`
    hence forward.

* Open the script [`$INSTALL_BASE_DIR/bin/generic-install.sh`](bin/generic-install.sh) and scan the header
  for required environment settings. 

* Set environment variables if applicable (or patch the script).

* Change to `root` and execute the script [`$INSTALL_BASE_DIR/bin/generic-install.sh`](bin/generic-install.sh)
