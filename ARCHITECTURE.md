![Under Construction Logo](doc/logo_under_construction_sign_wide.png)

This page is still under construction. Please, bear with me. Thanks!

![LittleBrother-Logo](little_brother/static/icons/icon_baby-panda_128x128.png)

# Architecture

*A more detailed description will follow in a while. For the time being this is the architecture in a nutshell:*

*   `LittleBrother` is  all-Python3 application running as a dedicated user `little-brother` (which is installed 
by the Debian package).

*   The application regularly scans the process list of the host for configured patterns and, if found, executes configured
rules. When not active it sleeps in a system interrupt.

*   If the maximum login time of users is exceeded the application will terminate the appropriate processes.

*   Process termination is done by a sudo-rule permitting the use of  `kill` for the user `little-brother`.

*   The web-interface which is based upon `flask` provides simple status information on the login times of the
monitored users and a simple administration interface to modify the more statically defined rules defining the 
maximum login times (and other parameters) of the users. The administration page is protected by a password.

*   When installed as a client-server application, an arbitrary number of client hosts will communicate with the master
host using a simple REST HTTP protocol.

*   The application itself and two supporting projects (`python_base_app` and `flask_helpers`) have configurations
to be packaged as PIP packages which are included in the Debian package.

*   The control script of the Debian package installs `pip3` and installs the included PIP packages and all other
required PIP packages from [pypi](https://pypi.org/).
