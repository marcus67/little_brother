![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)
<IMG SRC="doc/logo_under_construction_sign_wide.png" HEIGHT="128">

# Angular Web Frontend Manual
As of version 0.5.1 of LittleBrother a new Angular web frontend is being developed. It has not reached maturity
or full functionality yet. While it is still under construction the "classic" frontend will remain available.

However, it is already possible to activate both frontends simultaneously to get a glimpse of the new technology. 
To do  so, only a few extra settings have to be made in the configuration file. See the section ` [StatusServer]` 
of the [server configuration file](etc/master.config).

The usage of the new frontend will be very similar to the classic one, so we currently refrain from repeating
the documentation just with updated screenshots. However, since the functionality is currently only partially 
implemented, the following table shows the availability of the all aspects:

| Module  | Status              | Adaptive Behavior | International Support |
|---------|---------------------|-------------------|-----------------------|
| Login   | Available           | Missing           | Missing               |
| Status  | Available           | Missing           | Missing               | 
| Admin   | Available           | Missing           | Missing               |
| Users   | Partially available | Missing           | Missing               |
| Devices | Missing             | Missing           | Missing               |
| About   | Available           | Missing           | Missing               |

**NOTE**: Currently, both frontends of LittleBrother only support English as language. This was due to a simplified
merge of the two source code branches both using the Python Flask package to serve web pages. Hopefully, international 
support will soon be restored for the classic web frontend!
