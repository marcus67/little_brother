![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)
![LittleBrother-Logo](little_brother/static/icons/docker-logo-128x128.png)

# Docker Support for `LittleBrother`

## Overview

Currently, there is a [docker image](https://hub.docker.com/repository/docker/marcusrickert/little-brother-slave) 
available to run a LittleBrother slave process.

See [this repository](https://github.com/marcus67/docker-little-brother) for docker-compose support files. 
 

## Tag Naming Conventions

The tag names of the images are derived from the pattern `BRANCH-REVISION` where `BRANCH` is either `master` or
`release` and `REVISION` represents the number as listed in [changes](CHANGES.md). The special tag `latest` is used
for the most up-to-date release revision.

## Obsolete Security Details

The following aspects are obsolete since notifications should be issued by 
[LittleBrotherTaskbar](https://github.com/marcus67/little_brother_taskbar) now and no longer by the slave process.  

*   In order to be able to "speak" (that is play sound files), the process inside the container has to access the sound
device of the host. This is made possible by mounting the file `/etc/asound.conf` and the device `/dev/snd` 
into the container.

*   In order to be able to open message boxes as X clients, the X Windows device `/tmp/.X11-unix` is mounted into the 
container. The opening of the message boxes actually requires a second step. See [Using Popups](README.md#using-popups). 
Also, the environment variable `DISPLAY` is exported into the container. Make sure that the variable contains the 
X display identifier that is used by the users which are to be monitored by LittleBrother. In most cases this 
should be `:0.0` or `localhost:0.0`.
