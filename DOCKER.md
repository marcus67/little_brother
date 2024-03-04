![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)
![LittleBrother-Logo](little_brother/static/icons/docker-logo-128x128.png)

# Docker Support for `LittleBrother`

## Overview

Currently, there are four Docker images available for `LittleBrother`:
* [little-brother-client](https://hub.docker.com/repository/docker/marcusrickert/little-brother-client) 
  containing a LittleBrother client based on a Debian base image.
* [little-brother-ubuntu-client](https://hub.docker.com/repository/docker/marcusrickert/little-brother-ubuntu-client) 
  containing a LittleBrother client based on an Ubuntu base image.
* [little-brother-alpine-client](https://hub.docker.com/repository/docker/marcusrickert/little-brother-alpine-client) 
  containing a LittleBrother client based on an Alpine Linux base image. This is the smallest image for
  `LittleBrother`!
* [little-brother-slave](https://hub.docker.com/repository/docker/marcusrickert/little-brother-slave) 
  containing a LittleBrother client based on a Debian base image. This image is obsolete for naming reasons
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
