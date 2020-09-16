![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)
![CentOS-Logo](doc/centos-logo.png)
![OpenSuSe-Logo](doc/opensuse-logo.png)

# Installation on Non-Debian Distributions

If you don't have a Debian distribution running or at least a distribution using the Debian package format you
still may be able to install `LittleBrother` manually.

This page will outline how to do this.

## Prerequisites

Install the following Linux packages. Note that the exact names may differ in your distribution.

| Debian Package     | CentOS Package        | SuSe Package |
| ------------------ | --------------------- | ------------ |
|   `python3`        | `python3`             | TODO         |
|   `python3-pip`    | `python3-pip`         | TODO         |
|   `python-dev`     | `python2-devel`       | TODO         |
|   `python3-dev`    | `python3-devel`       | TODO         |
|   `sudo`           | `sudo`                | TODO         |
|   `gcc`            | `gcc`                 | TODO         |
|   `procps`         | `procps-ng`           | TODO         |
|   `virtualenv`     | `python3-virtualenv`  | TODO         |

## Installation Steps

*   Download the current GitHub project as a 
    [zipped tar file](https://github.com/marcus67/little_brother/archive/master.zip) and store it locally.
    
*   Unzip the archive by executing `unzip master.zip`.

*   The base directory of the unzipped archive containing the `README.md` will be referenced as `$INSTALL_BASE_DIR`
    hence forward.

*   Download the current PIP3 packages for `LittleBrother`, `python_base_app` and `some_flask_helpers` from 
    the test PyPi repository using these links 
    
    *   [LittleBrother](https://test.pypi.org/project/little-brother/#files) 
    *   [python_base_app](https://test.pypi.org/project/python-base-app/#files) 
    *   [some_flask_helpers](https://test.pypi.org/project/some-flask-helpers/#files) 
    
    and store a copy of them into `/tmp`.
    Note: By default, these three files are included in the Debian package.
*   Change to `root` and execute the script `$INSTALL_BASE_DIR/bin/generic-install.sh`
