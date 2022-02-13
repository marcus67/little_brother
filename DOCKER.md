![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)
![LittleBrother-Logo](little_brother/static/icons/docker-logo-128x128.png)

# Docker Support for `LittleBrother`

## Overview

Currently, there are three Docker images available for `LittleBrother`:
* [little-brother-client](https://hub.docker.com/repository/docker/marcusrickert/little-brother-client) 
  containing a LittleBrother client process based on a Debian base image.
* [little-brother-ubuntu-client](https://hub.docker.com/repository/docker/marcusrickert/little-brother-ubuntu-client) 
  containing a LittleBrother client process based on an Ubuntu base image.
* [little-brother-slave](https://hub.docker.com/repository/docker/marcusrickert/little-brother-slave) 
  containing a LittleBrother client process based on a Debian base image. This image is obsolete for naming reasons
  and **will not be updated**. Please, migrate to one of the images above.

See [this repository](https://github.com/marcus67/docker-little-brother) for docker-compose support files. 

## Tag Naming Conventions

The tag names of the images are derived from the pattern `BRANCH-REVISION` where `BRANCH` is either `master` or
`release` and `REVISION` represents the number as it is listed in [changes](CHANGES.md). The special tag `latest` 
is used for the most up-to-date release revision.

## Obsolete Security Details

The following aspects are obsolete since notifications should be issued by 
[LittleBrotherTaskbar](https://github.com/marcus67/little_brother_taskbar) now and no longer by the client process.  

*   In order to be able to "speak" (that is play sound files), the process inside the container has to access the sound
device of the host. This is made possible by mounting the file `/etc/asound.conf` and the device `/dev/snd` 
into the container.

*   In order to be able to open message boxes as X clients, the X Windows device `/tmp/.X11-unix` is mounted into the 
container. The opening of the message boxes actually requires a second step. See [Using Popups](README.md#using-popups). 
Also, the environment variable `DISPLAY` is exported into the container. Make sure that the variable contains the 
X display identifier that is used by the users which are to be monitored by LittleBrother. In most cases this 
should be `:0.0` or `localhost:0.0`.
