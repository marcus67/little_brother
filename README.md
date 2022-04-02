![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)

# Parental Control Application `LittleBrother`

## Overview

`LittleBrother` is a simple parental control application monitoring specific processes (read "games") on Linux hosts
to monitor and limit the play time of (young) children. It is designed as a client server application running
on several hosts and combining playing time spent across these hosts, but it also works on a standalone host.

When the application determines that a user has exceeded her play time, it will terminate the running 
process. Usually, the user will get several spoken notifications (using the 
[LittleBrotherTaskbar](https://github.com/marcus67/little_brother_taskbar)) before she is actually kicked out so 
that she can log out gracefully in time.

## What's New?

The latest major feature changes are:

| Version  | Feature/Fix                                                   | (Issue) Link                                                         |
|----------|---------------------------------------------------------------|----------------------------------------------------------------------|
| 0.4.23   | Optionally use `iptables` to restrict network access          | [Issue 169](https://github.com/marcus67/little_brother/issues/169)   |
| 0.4.20   | *Bug Fix*: Use Python virtual environment again               | [Issue 170](https://github.com/marcus67/little_brother/issues/170)   |
| 0.4.17   | *Bug Fix*: Remove incompatibility with new `alembic` version  | [Issue 166](https://github.com/marcus67/little_brother/issues/166)   |
| 0.4.16   | *Bug Fix*: Ignore invalid hosts during ping                   | [Issue 165](https://github.com/marcus67/little_brother/issues/165)   |
| 0.4.15   | *Bug Fix*: Do not fail on Debian package upgrades             | [Issue 158](https://github.com/marcus67/little_brother/issues/158)   |
| 0.4.14   | *Bug Fix*: Correct detection of users in master-only setups   | [Issue 163](https://github.com/marcus67/little_brother/issues/163)   |
| 0.4.12   | *New*: Client process available as snap                       | [Snapcraft Support](https://github.com/marcus67/snap-little-brother) |
| 0.4.9    | *New*: Automatic check for new versions of `LittleBrother`    | [Issue 150](https://github.com/marcus67/little_brother/issues/150)   |
|          | *Improvement*: Separate LDAP search DN for groups and users   | [Issue 144](https://github.com/marcus67/little_brother/issues/144)   |
|          | *Improvement*: Cache timeout for LDAP data                    | [Issue 138](https://github.com/marcus67/little_brother/issues/138)   |
| 0.4.8    | *New*: Full support for requesting optional time by users     | [Issue 130](https://github.com/marcus67/little_brother/issues/130)   |
| 0.4.4    | *New*: Use user specific patterns to prohibit applications    | [Issue 129](https://github.com/marcus67/little_brother/issues/129)   |

## Contact

Visit the project at [Facebook](https://www.facebook.com/littlebrotherdebian) or write comments 
to little-brother(at)web.de.

## Screenshots

The following screenshots show the web frontend of `LittleBrother`. Click on the thumbnails to enlarge. 

<A HREF="doc/screenshot_status.png">![Screenshot Status](doc/screenshot_status.thumb.png)</A> 
<A HREF="doc/screenshot_login.png">![Screenshot Status](doc/screenshot_login.thumb.png)</A> 
<A HREF="doc/screenshot_admin.png">![Screenshot Status](doc/screenshot_admin.thumb.png)</A> 
<A HREF="doc/screenshot_users.png">![Screenshot Status](doc/screenshot_users.thumb.png)</A> 
<A HREF="doc/screenshot_devices.png">![Screenshot Status](doc/screenshot_devices.thumb.png)</A> 
<A HREF="doc/screenshot_topology.png">![Screenshot Status](doc/screenshot_topology.thumb.png)</A>
<A HREF="doc/screenshot_about.png">![Screenshot Status](doc/screenshot_about.thumb.png)</A>

## Change History 

See [here](CHANGES.md)

## GitHub Status

<A HREF="https://github.com/marcus67/little_brother">
<IMG SRC="https://img.shields.io/github/forks/marcus67/little_brother.svg?label=forks"></A> 
<A HREF="https://github.com/marcus67/little_brother/stargazers">
<IMG SRC="https://img.shields.io/github/stars/marcus67/little_brother.svg?label=stars"></A> 
<A HREF="https://github.com/marcus67/little_brother/watchers">
<IMG SRC="https://img.shields.io/github/watchers/marcus67/little_brother.svg?label=watchers"></A> 
<A HREF="https://github.com/marcus67/little_brother/issues">
<IMG SRC="https://img.shields.io/github/issues/marcus67/little_brother.svg"></A> 
<A HREF="https://github.com/marcus67/little_brother/pulls">
<IMG SRC="https://img.shields.io/github/issues-pr/marcus67/little_brother.svg"></A>

## SourceForge Download Status

<a href="https://sourceforge.net/projects/little-brother/files/latest/download">
<img alt="Download little-brother" src="https://img.shields.io/sourceforge/dm/little-brother.svg"></a>

## Continuous Integration Status Overview

| Status              | Master                                                                                                                                                                                                                                                                                                                                                               | Release                                                                                                                                                                                                                                                                                                                                                              |
|:------------------- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |:-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| CircleCI            | <A HREF="https://circleci.com/gh/marcus67/little_brother/tree/master"><IMG SRC="https://img.shields.io/circleci/project/github/marcus67/little_brother/master.svg?label=master"></A>                                                                                                                                                                                 | <A HREF="https://circleci.com/gh/marcus67/little_brother/tree/release"><IMG SRC="https://img.shields.io/circleci/project/github/marcus67/little_brother/release.svg?label=release"></A>                                                                                                                                                                              |
| Test Coverage       | <A HREF="https://codecov.io/gh/marcus67/little_brother/branch/master"><IMG SRC="https://img.shields.io/codecov/c/github/marcus67/little_brother.svg?label=master"></A>                                                                                                                                                                                               | <A HREF="https://codecov.io/gh/marcus67/little_brother/branch/release"><IMG SRC="https://img.shields.io/codecov/c/github/marcus67/little_brother/release.svg?label=release"></A>                                                                                                                                                                                     |
| Codacy Code Quality | <A href="https://www.codacy.com/app/marcus67/little_brother?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=marcus67/little_brother&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/3e3130c1c450404db9b16e10ab8af7fd"/></a>                                                                                         | <A href="https://www.codacy.com/app/marcus67/little_brother?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=marcus67/little_brother&amp;utm_campaign=Badge_Grade"><img src="https://api.codacy.com/project/badge/Grade/3e3130c1c450404db9b16e10ab8af7fd?branch=release"/></a>                                                                          |
| Code Climate        | <a href="https://codeclimate.com/github/marcus67/little_brother/maintainability"><img src="https://api.codeclimate.com/v1/badges/c42e65d566d1e10f1402/maintainability" /></a>                                                                                                                                                                                        | not available                                                                                                                                                                                                                                                                                                                                                        |
| Snyk Vulnerability  | <A href="https://snyk.io/test/github/marcus67/little_brother?targetFile=requirements.txt"><img src="https://snyk.io/test/github/marcus67/little_brother/badge.svg?targetFile=requirements.txt" alt="Known Vulnerabilities" data-canonical-src="https://snyk.io/test/github/marcus67/little_brother?targetFile=requirements.txt" style="max-width:100%;"></a>         | <A href="https://snyk.io/test/github/marcus67/little_brother?targetFile=requirements.txt"><img src="https://snyk.io/test/github/marcus67/little_brother/release/badge.svg?targetFile=requirements.txt" alt="Known Vulnerabilities" data-canonical-src="https://snyk.io/test/github/marcus67/little_brother?targetFile=requirements.txt" style="max-width:100%;"></a> |
| Snyk Package Health | not available                                                                                                                                                                                                                                                                                                                                                        | [![little-brother](https://snyk.io/advisor/python/little-brother/badge.svg)](https://snyk.io/advisor/python/little-brother)                                                                                                                                                                                                                                          |

Note: The vulnerability status is derived from the Python PIP packages found in `requirements.txt`.

## Features

`LittleBrother` has the following features:

*   Any number of users can be monitored.

*   Each user can have a specific set of rules defining the permitted playtime.

*   Rules can be adapted to "contexts", such as the day of the week and/or a vacation schedule (currently only 
the German schedules are supported).

*   Play time can be restricted to a time window (from, to).

*   A maximum play time per day can be defined.

*   Users can be forced to take a break after a certain maximum session time.

*   Users can be forced to wait for a minimum break time after their activity.

*   Any number of Linux client hosts can be monitored.

*   There is a master host with a history of the activities of all users. This master host checks the rule sets and
prompts the client hosts to terminate processes if required.

*   The master host offers a simple web interface for viewing the user activity over a configured history length
(e.g. 7 days) and an administration page to dynamically define rule exceptions for a configured number of
days into the future.

*   The web application can be run behind a proxy so that it will be accessible from away allowing remote 
administration after receiving calls from young users begging for more play time.

*   There is a helper application ([LittleBrotherTaskbar](https://github.com/marcus67/little_brother_taskbar)) to 
display the remaining playtime of a monitored user and speak the notifications.

*   The application has international language support. Currently English, Italian and German translations are provided.
Users are invited to provide translations for other languages.

*   Downtime of a server during playtime (e.g. due to hibernation) is automatically subtracted from the play time.

*   In addition to the time spent on Linux hosts the application can also monitor activity time on other devices 
such as smartphones or tables. It takes advantage of the fact that most modern operating systems put devices
in some kind of power saving mode while they are not being used. This way, the network response (by `pinging`) can
be used to determine the activity on those devices. In contrast to the Linux hosts, the application
will not be able to terminate the activity. The play time, however, will be added to the overall playtime and
hence will have an impact on the time allowed and also on the break time rules on the Linux hosts.

*   As of version 0.3.12 `LittleBrother` is able to use [ProxyPing](https://github.com/marcus67/proxy_ping) to ping
devices behind firewalls provided the tool can be deployed on a Debian server behind the firewall.

*   As of version 0.3.13 `LittleBrother` clients will terminate local user sessions if they cannot reach the master
process for a certain time (defaults to 50 seconds). This ensures users cannot suppress being logged out by 
*pulling the plug*.

*   As of version 0.4.0 `LittleBrother` provides an administration feature to easily extend the current computer time 
or grant computer when the usage would normally be prohibited. This is called a time extension. During an active 
extension all other restrictions (maximum time per session, time of day, and maximum time per day) are deactivated.
Time extension can even extend into the next day making long night session possible. However, any computer time
actually spent during a time extension will contribute to the overall time played in the course of a day.   

*   There is a Docker image available (currently for the client only) which makes it really easy to run a client on a 
Linux host with a Docker daemon available.

*   The application uses voice generation to inform the user over impending logouts. Also, these spoken
messages are internationalized. Optionally, users can be notified using four different popup tools. Note that this
functionality of the `LittleBrother` application has been replaced by the `LittleBrotherTaskbar.` 

## Architecture

The [page](ARCHITECTURE.md) gives a detailed description of the architecture of the application.    

## Tested Distributions

So far, `LittleBrother` has only been released as a Debian package. For other non-Debian based distributions 
there is some basic support using a generic installation script. 
See [this page](NON-DEBIAN-INSTALLATION.md) for details.

| Distribution | Version       | Architecture | Comments                                                                                                                                                     | Most Recent Test |
| ------------ | ------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------ | ---------------- |
| Ubuntu       | 20.04         | amd64        | This version is used as base image for the [Ubuntu Docker image](https://hub.docker.com/repository/docker/marcusrickert/little-brother-ubuntu-client)        | 28.JAN.2022      |
| Debian       | 11 (bullseye) | amd64        | Feedback from a user as regular install using Mate desktop                                                                                                   | 06.MAR.2022      |
| Ubuntu       | 18.10         | amd64        | See [pip3 issue](https://github.com/marcus67/little_brother/issues/53)                                                                                       | 03.JUN.2019      |
| Debian       | buster        | amd64        | The version `buster-slim` is used as base image for the [Debian Docker image](https://hub.docker.com/repository/docker/marcusrickert/little-brother-client)  | 01.JAN.2020      |
| Debian       | 10.3 (buster) | amd64        | Feedback from a user as regular install with Mate desktop                                                                                                    | 05.MAR.2020      |
| Mint         | 19            | amd64        |                                                                                                                                                              | 03.JAN.2020      |
| Arch Linux   |               | amd64        | See https://aur.archlinux.org/packages/little-brother                                                                                                        | 06.MAR.2022      |
| Debian       | stretch       | armv6l       |                                                                                                                                                              | 23.MAY.2020      |
| Alpine       | v3.13         | amd64        | This distribution is used as base image for the [Alpine Docker Image](https://hub.docker.com/repository/docker/marcusrickert/little-brother-alpine-client)   | 06.MAR.2022      |

## Quick Install (Snap)

There is a snap available for the client process. See [snap-little-brother](https://github.com/marcus67/snap-little-brother) for details. 

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/little-brother-slave)

## Quick Install (Debian Package)

This guide will take you through the steps required to install, configure, and run the `LittleBrother` application 
on your system. This guide works both for master and client setups. For setting up a client there is a second option
using Docker. See the [Docker](DOCKER.md) page for more details.

### YouTube Videos

| Thumbnail and Link to Video                                                                                                                                                  | Duration | Content                                                                                      | Related Versions                          |
| ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------- | -------------------------------------------------------------------------------------------  | ----------------------------------------- |
| <A HREF="https://www.youtube.com/watch?v=gOxUBlfKZyM">![little-brother-0_3_1](doc/youtube-presentations/2020-07-30_LittleBrother_YouTube_Presentation.thumb.png) </A>        | 16 min   | Install LittleBrother Debian package, edit configuration file, add user, test functionality  | LittleBrother 0.3.1 on Ubuntu 19.3        |
| <A HREF="https://www.youtube.com/watch?v=vLqho7oRNi4">![little-brother-0_3_1](doc/youtube-presentations/2020-08-07_LittleBrotherTaskbar_YouTube_Presentation.thumb.png) </A> | 14 min   | Install LittleBrotherTaskbar pip3 package, register desktop service, test functionality      | LittleBrotherTaskbar 0.1.9 on Ubuntu 19.3 |

### Download the Software

The application is available as a Debian package 
from the [`release`](https://sourceforge.net/projects/little-brother/files/release/) directory at SourceForge. 
The latest build is available from the [`master`](https://sourceforge.net/projects/little-brother/files/master/) 
directory. Install it as you would install any other Debian package with

    dpkg -i PACKAGE.deb
    apt-get install -f

Note that the second command is required to install missing dependencies since `dpkg` does not run a dependency check.
Instead, it will return with an error which will then be "fixed" by `apt-get`. 

After installation use

    systemctl start little-brother

to start the application right away. The application will 
successfully start up provided that the default port 5555 is available on the host. You can check the success by trying 
to log into the [web frontend](http://localhost:5555/).

### Configuring the Application (Mostly Optional)

The default setup will fit most first-time users (except for the password). The following table contains 
various additional aspects that may require additional configuration.

| Aspect                      | Default Setting                                                            | Alternatives                                                    | Reference                                               |
| --------------------------- | -------------------------------------------------------------------------- | --------------------------------------------------------------- | ------------------------------------------------------- |
| Admin Password              | User `admin` with password `test123`                                       | Use LDAP for authentication and authorization                   | See "Setting Admin Password" below                      | 
| Database backend            | File oriented database [sqlite](https://www.sqlite.org/index.html)         | Full fledged database such as MySQL dor MariaDB                 | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Web frontend port           | `5555`                                                                     | Any other available port                                        | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Web frontend base URL       | `/`                                                                        | Any other path                                                  | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| User registry               | `/etc/passwd`                                                              | Predefined users and UIDs or LDAP registry                      | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Master client setup         | Use only a master host                                                     | Use any number of client hosts                                  | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Mapping UIDs                | UIDs are synchronized across all hosts                                     | Each host (group) can have different UIDs                       | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Scanning Interval           | Every 5 seconds                                                            | Any other interval                                              | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Reverse proxy setup         | No reverse proxy                                                           | Run little-brother behind a reverse proxy (e.g. `nginx`)        | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Docker Support              | Client is installed as Debian package                                      | Client is run as Docker container                               | See [Docker](DOCKER.md).                                |
| Prometheus Support          | Not activated                                                              | Activate Prometheus server port and provide run time statistics | See [Operational Monitoring](OPERATIONAL_MONITORING.md).|
| Network Tempering Detection | Automatic logout of monitored users after a network downtime of 50 seconds | Set a different time out                                        | See [Advanced Configuration](ADVANCED_TOPICS.md)        |
| Firewall support            | Do not restrict network access of client hosts                             | Configure targets IP addresses to be blocked                    | See [Advanced Configuration](ADVANCED_TOPICS.md)        |

### Setting the Admin Password

For the time being setting the admin password is the only standard configuration that still requires using an editor.
See this [issue](https://github.com/marcus67/little_brother/issues/92).
You have to be `root` to follow these steps (e.g. use `sudo`):
 
*   Use your favorite editor to edit the file `/etc/little-brother/little-brother.conf`.

*   Find the setting `admin_password` in the section `[UnixUserHandler]`.

*   Change the password.

*   Save the file.

*   Restart the application by issuing: 

        systemctl restart little-brother 

From now on the new password will have to be used to access the administration pages.

### Using the Web-Frontend

You are all set now. It's time to set up users to be monitored and optionally devices. See the 
[Web Frontend Manual](WEB_FRONTEND_MANUAL.md). 

### Troubleshooting

So, you went through all the above but LittleBrother does not seem to work? Maybe this 
[troubleshooting page](TROUBLESHOOTING.md) can help you.

## Caveats

The application `LittleBrother` is far from perfect. Some major caveats are listed here and/or in the 
issue list on GitHub (see [here](../issues)).

*   Every once in a while processes fail to terminate even though they have been killed by `LittleBrother`. 
In these cases the user will still be regarded as logged in although he/she is not. Usually this can only be
solved by trying to kill the processes again using the master user. Database eloquent users may try to 
delete/correct the incorrect process time entries.

*   The web server only responds to HTTP requests. This is probably always OK for communication between the
clients and the master in local area network. If the master host is to be accessible from the internet, it should
be put behind a reverse proxy handling the HTTPS termination (see below). 

## Internationalization

The application uses the PIP package `Flask-Babel` to provide internationalization for the web frontend. Currently, 
the following languages are supported or in preparation (in the order they were made available):

| Flag                                                           | Language      | Locale | Status         | Translation provided by    |
| ---------------------------------------------------------------| ------------- | ------ | -------------- | ---------------------------|
| ![Flag USA](doc/united-states-of-america-flag-icon-32.png)     | English       | en     | Up-to-date     |  Marcus Rickert            |
| ![Flag Germany](doc/germany-flag-icon-32.png)                  | German        | de     | Up-to-date     |  Marcus Rickert            |
| ![Flag Italy](doc/italy-flag-icon-32.png)                      | Italian       | it     | Revision 116   |  Albano Battistella        |
| ![Flag Netherlands](doc/netherlands-flag-icon-32.png)          | Dutch         | nl     | Revision 63    |  Simone & Lex              |
| ![Flag Finland](doc/finland-flag-icon-32.png)                  | Finnish       | fi     | Revision 63    |  Isakkii Kosonen           |
| ![Flag France](doc/france-flag-icon-32.png)                    | French        | fr     | Revision 86    |  Albano Battistella        |
| ![Flag Turkey](doc/turkey-flag-icon-32.png)                    | Turkish       | tr     | Revision 63    |  Selay Dogan               |
| ![Flag Russia](doc/russia-flag-icon-32.png)                    | Russian       | ru     | Revision 63    |  J. Moldawski              |
| ![Flag Japan](doc/japan-flag-icon-32.png)                      | Japanese      | ja     | Revision 63    |  Arik M.                   |
| ![Flag Bangladesh](doc/bangladesh-flag-icon-32.png)            | Bangla        | bn     | Revision 63    |  Rownak Jyoti Zaman        |
| ![Flag Thailand](doc/thailand-flag-icon-32.png)                | Thai          | th     | Revision 63    |  Busaba Kramer             |
| ![Flag Denmark](doc/denmark-flag-icon-32.png)                  | Danish        | da     | Revision 63    |  Erik Husmark              |
| ![Flag Spain](doc/spain-flag-icon-32.png)                      | Spanish       | es     | Revision 63    |  Ruth Wucherpfennig-Krömer |
| ![Flag Croatia](doc/croatia-flag-icon-32.png)                  | Croatian      | hr     | Revision 63    |  Incognito                 |
| ![Flag Lithuania](doc/lithuania-flag-icon-32.png)              | Lithuanian    | lt     | In preparation |  N.N.                      |

A revision number in the status column denotes that all texts up to that revision have been localized.
 
Your help with translations is greatly appreciated. Please, contact the author if you are interested in providing
a translation. You do not necessarily have to clone this repository or be familiar with Python to do so.

## Credits

*   Thanks to all the people maintaining the wonderful script language [Python](https://www.python.org/) 
    and the libraries on [PyPi](https://pypi.org/).

*   The country flags were taken from [www.countryflags.com](https://www.countryflags.com/).

*   See the section about on internationalization for credits regarding the translations.

*   The site [www.mehr-schulferien.de](https://www.mehr-schulferien.de) maintains the vacation metadata for
    Germany.
    
*   The icons are provided by [fontawesome.com](https://fontawesome.com).

*   People contributing by providing pull requests:

    * [Bas Hulsken](https://github.com/bhulsken)
      * See [issue 120](https://github.com/marcus67/little_brother/issues/120)
      * See [issue 166](https://github.com/marcus67/little_brother/issues/166)
    * [Albano Battistella](https://github.com/albanobattistella) for providing Italian and French translations 
