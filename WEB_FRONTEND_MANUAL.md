![Under Construction Logo](doc/logo_under_construction_sign_wide.png)

This page is still under construction. Please, bear with me. Thanks!

![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)

# Web-Frontend Manual

This page describes the web frontend of `LittleBrother` which usually can be reached at 
[http://localhost:5555](http://localhost:5555) on your local machine. It offers access to status information (without
login() and a configuration interface (with login). 

## Listing the Status

![Menubar-Status](doc/menubar-status.png)

The menu entry "Status" list the play times of all monitored users. The top level shows the summary of the play times
of the current monitored users.

![Status-Level-1](doc/status-level-1.png)

A blinking entry denotes an active login. In case the user is currently allowed to play (see green check mark) the 
column "reasons" shows the estimated remaining play times for the current session (if logged in) and for the day.
If the user is currently blocked (see red cross) the same column shows the reasons why the user is not permitted to 
play and the estimated remaining play time for the day.
   
![Status-Reasons](doc/status-reasons.png)
     
The second level can be opened by clicking on the name of a user. It will show the daily play time, the number 
of logins and the hosts of the last seven days of the selected user.

![Status-Level-2](doc/status-level-2.png)

The third level can be opened by clicking on a day summary of a user. It will show the individual play times and
hosts of the selected user on the selected day. The entries are sorted by the start time in descending order with
the most recent entry at the top.   

![Status-Level-3](doc/status-level-3.png)

## About Page

![Menubar-About](doc/menubar-about.png)

The page shows some status information of the installed version of `LittleBrother` and a list of supported languages.

![Menubar-About](doc/about.png)  

## Logging In

The status page and the about page are accessible without login. All other pages require the login credentials of
an administration user. Currently, the name of the administration user defaults to `admin`. The password needs to
be set in the configuration file (see the main [README](../README.md)).

![Login](doc/login.png)  

After successful login the user will be display in the menu bar.

![Login](doc/login-status.png)  

## Administration

![Menubar-Admin](doc/menubar-admin.png)

The administration page enables the user to override the default restrictions for the monitored users. This is possible 
for the current day and up to 7 days into the future.

The top level shows the names and today's activity of the current monitored users.
In case the user is currently allowed to play (see green check mark) the 
row shows the estimated remaining play times for the current session (if logged in) and for the day.
If the user is currently blocked (see red cross) the row shows the reasons why the user is not permitted to 
play and the estimated remaining play time for the day.

![Admin-Level-1](doc/admin-level-1.png)
   
The second level can be opened by clicking on the name of a user. It will show the active restrictions of
the current day and the next seven days of the selected user. The column "Context" denotes which ruleset is active
on the respective day. The entries are sorted by the start time in ascending order with
the current day at the top.

![Admin-Level-2](doc/admin-level-2.png)

The third level can be opened by clicking on a day row. It will show input fields to override the default
restrictions of the active ruleset of the selected day.    

![Admin-Level-3](doc/admin-level-3.png)

To override settings enter the desired values and click the save button.

![Save-Button](doc/save-button.png)

Most of the input fields require a certain input format. If the values violate the format, 
a validation message will be displayed. All errors have to be taken care of before the settings will be saved.

![Admin-Level-3](doc/admin-validation-message.png)

When default values are overridden the day row shows the values in blue color. Removing the overriding values 
removes the color again. 

![Admin-Override](doc/admin-override.png)

## Configuring Users

![Menubar-Status](doc/menubar-users.png)

Before a user can be monitored she has to be added to the users list of `LittleBrother`. After installation the
users list is empty. The application will try to retrieve the users on the master host by querying the 
`/etc/passwd` file using standard Python libraries. See [Users and UIDs in README](README.md) for details. 

All users found that are not being monitored yet will be offered in the drop down menu following "Add to monitoring":

![Menubar-Status](doc/users-add-user-list.png)

To add the user choose the user name from the drop down list and click the add button:

![Add-Button](doc/add-button.png)

After the user has been added her top level entry will be shown:

![Menubar-Status](doc/users-new-user-added.png)

Click on the username to change to second level of the user entry:

![Menubar-Status](doc/users-level-1.png)

The details will show the following items:

*   *Monitored*: denotes if the user will actually be monitored. This will be un-ticked for all new users and should 
only be ticked off after the user has been configured completely using rulesets and optionally devices.

*   *First Name*: sets the first name of the user. When set the first name will be used in notifications instead of the
username which may be unpronounceable. 

*   *Last Name*: sets the last name of the user. This is only used as label in lists.

*   *Locale*: sets the language in which notifications are spoken to the user. The locale will be passed on to the
tool [LittleBrotherTaskbar](https://github.com/marcus67/little_brother_taskbar) to this purpose. For a new user
the locale always defaults to the locale which is detected from the browser.

*   *Process Name Pattern*: sets a regular expression defining the processes which represents a "login" by the user. 
The default value comprises all standard shells and `systemd` which is started by login process using X11. Only change
this setting if you absolutely know what you are doing.
 
### Adding Rulesets

When a new user is created, there is always one default rule created for her which will act as a fallback if no other
rule applies. However, the new rule does not contain any restrictions yet:

![Menubar-Status](doc/users-rulesets-level-2.png)

Use the entry fields to optionally change the default settings:

![Menubar-Status](doc/users-rulesets-level-2-filled-in.png)

The fields represent the following restrictions/meaning:

*    *LabeL*: changes the default label of the rule in lists and messages.

*    *Context*: sets the context (type) of rule. Currently, there are three contexts available. See below.

*    *Context details*: sets the specific details of the chosen context. See below.

*    *Min Time of Day*: optionally sets the earliest time of the day when login is allowed. Timestamps must be given 
in the format `HH:MM` in military time. Time durations must given in the format `HHh:MMm`.  Either part may be omitted 
and the minutes may exceed 60.
   
*    *Max Time of Day*: optionally sets the latest time of the day when login is allowed. The format is same as above.  

*    *Time per Day*: optionally sets the duration that the user is allowed to be logged in (for the whole day). 
The format mus be `HHh:MMm` for `HH` hours and `MM` minutes. Either part can be omitted.  

*    *Minimum Break*: optionally sets a mandatory break time between sessions. The format is the same as above.

*    *Max Duration*: optionally sets the maximum length of a session. The format is the same as above.

*    *Free Play*: If ticked, the user is allowed to play without any restrictions. Any other restriction in the same
rule will be suppressed.

### Computing the Break Time

When there is a maximum session time and a minimum break time configured for a rule `LittleBrother` tries to compute
a *fair* break duration as follows:

*    If a user has played her full maximum session time the whole configured break time will apply.
*    If a user has played less than her maximum session time the break time will be enforced proportionally that is
the effective break time compared to the configured break time will have the same ratio as the actual session time
to the maximum session time. Example: the maximum session time is set to 1 hour and the break time to 30 minutes. The
user decides to play for 40 minutes in her session which accounts for two thirds of the maximum session time. Hence
the break time will be `2/3*30=20` minutes.    

### Rule Contexts

Each rule can be seen as a day selector. If all days are to be treated equally one rule should do the job. 

If different days are to be treated differently more rules are required besides the default *catch all* rule. 
To this purpose the setting `context` can be used. If its value is `weekday` the setting
`context_details` will contain either:

*   the concrete name of the day of the week,

*   the string `weekend` comprising Saturday and Sunday, or day-coded seven-character string in which `1`, `X`, or `Y` 
denotes an active day and any other character denotes an inactive day. For example: the string "X-X-X--" would denote 
a rule which is active on Mondays, Wednesdays, and Fridays. 

If the value of `context` is `german-vacation-calendar` the rule is active for all vacation days of a specific 
federal state in Germany. In this case the value of `context_details` denotes the name of the federal state:

*   `Baden-Württemberg`,
*   `Bayern`,
*   `Berlin`,
*   `Brandenburg`,
*   `Bremen`,
*   `Hamburg`,
*   `Hessen`,
*   `Mecklenburg-Vorpommern`,
*   `Niedersachsen`,
*   `Nordrhein-Westfalen`,
*   `Rheinland-Pfalz`,
*   `Saarland`,
*   `Sachsen`,
*   `Sachsen-Anhalt`,
*   `Schleswig-Holstein`, or
*   `Thüringen`.

### Assigning Devices to Users

## Configuring Devices

### Adding Devices

In addition to the processes of the Linux host the application `LittleBrother` can be configured to monitor 
activity on other devices by using the ICMP protocol (`ping`). The assumption is that when a device returns a 
quick response to ping it is currently active (or rather has an active user logged in). If, on the other hand,
the response is slow or if there is no response at all the device is regarded as inactive.

Using a `[ClientDevice*]` section it is possible to configure the scanning of device by giving its DNS name or 
IP address in the field `hostname` as in the example below.

    [ClientDeviceIPhoneUser2]
    name= iphone_user2
    username = user2
    hostname = iphone-user2.my-domain
    sample_size = 10
    min_activity_duration = 60
    max_active_ping_delay = 90

The entry is linked to the `username` on the Linux host. The field `min_activity_duration` denotes how many 
seconds a ping has to be responsive before the host is regarded as active. The field `max_active_ping_delay` 
denotes the maximum response time (measured in milliseconds) a ping may have to still be regarded as 
responsive. The effective delay is computed as moving average over the past `sample_size` response times.

Note that `LittleBrother` is not able terminate any processes on the monitored devices so that the users
may easily exceed their permitted access times there. However, any login times on these devices are added to
the access times on the Linux hosts so that the remaining access time is still influenced. Also, the minimum
break time will apply the point of time when the last other device became inactive.      
  
