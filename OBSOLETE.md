![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)

# Obsolete Features

This page describes features which are now obsolete.

## Using Popups

The popups described below are obsolete. They have been replaced by the 
[LittleBrotherTaskbar](https://github.com/marcus67/little_brother_taskbar). 

It is possible to activate popups to nofify the user about impending logouts. See the section `[PopupHandler]` 
in the configuration file (e.g. <A HREF="etc/minimal-slave.config">`minimal-slave.config`</A>).
 
The application knows how to handle four different X11 popup tools:

*   `yad`
*   `gxmessage`
*   `zenity`
*   `yad`

The chosen tool must be available on the respective client. If applicable, install the
Debian package having the same name, e.g. to install `yad` enter

    sudo apt-get install yad

Moreover, the user who is supposed to receive the popup messages has to give permission to create X11 clients
using a call to `xhost`:

    xhost +SI:localuser:little-brother

This statement must be added to the appropriate session startup script used on the host. This is a little tricky
since the specific file depends on the windows manager and/or login manager.

These are some good locations:

| Windows Manager | Filename  |
| --------------- | ---------
| Mate            | ~/.materc | 

## Old YouTube Videos

There is a YouTube video showing the installation of the pre-0.3 versions:

<A HREF="https://www.youtube.com/watch?v=Skb5Hz0XZuA"><IMG SRC="doc/youtube-presentations/2019-06-09_LittleBrother_YouTube_Presentation.thumb.png"></A>
