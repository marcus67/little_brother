![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)

# Troubleshooting `LittleBrother`

This page tries to help you with troubleshooting the most common problems with running LittleBrother. 

## The monitored user is not logged in but LittleBrother still shows her as active.

This is usually due to processes that do not get cleanly killed when the user logs out. One of the culprits may
be the `geoclue` daemon. Use 

    ps uax|grep geoclue

in a terminal to find out if there are any agents running. 
Chances are that you do not require `geoclue` on your system. In this case uninstalling the package using

    apt-get remove geoclue-2.0

may be an option for you.

## The web page is working, but I cannot see any activity of the monitored users

*   Check that the usernames used in the configuration file actually identically match the users that you would 
    like to monitor.

*   Check that the process name patterns actually match the processing starting on your host when the monitored users
    log in. Since there are so many flavours of Linux and window managers and X11 start up scripts this may be more 
    tricky than expected. The default pattern watches for shells (`.*sh`) for terminal login and for a typical login 
    process (`systemd`) when X11 is used to login but this may not apply to your system. Try the following:

    *   Since most attempts will most likely use the X11 login try to log into a shell instead by typing
  
        `ssh -l [USER] localhost`
      
        and check if this makes a difference. The placeholder `[USER]` will have to be replaced by the username of a 
        monitored user.
    
    *   If this works the origin of the problem is probably the process pattern used for the X11 login. In this case
        log into X11 using a monitored user. Open a shell (preferably by switching to a virtual text terminal first and 
        using a non-monitored login but if you are not familiar with this it's OK to start a terminal as the logged in 
        user) and type the following
    
        `ps uax|grep [USER]`
       
        Again the placeholder will have to be replaced. The list will show the processes created during X11 login. 
        If there is no `systemd` entry this will be the cause of the problem. Try to identify a different process name 
        that you find in the list and use that in the `process_name_pattern=` setting instead. If in doubt open a 
        ticket [here](../issues) or write mail to  little-brother(at)web.de to get help. Include the process list, 
        please, after removing any potentially sensitive information from it (e.g. passwords).    

## Error `AttributeError: Module Pip has no attribute 'main'` during Debian Package installation 

This is most likely due to a version mismatch or an outdated version of `pip`. Try this:

     rm -rf /var/lib/little-brother/virtualenv/
     apt-get update
     apt-get install python3-setuptools python3-pip
     apt-get install -f
     
The last step will probably not be necessary because the previous `apt-get` has already made a second attempt
at installing `little-brother`. 
