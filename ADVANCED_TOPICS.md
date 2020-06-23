![LittleBrother-Logo](little_brother/static/icons/icon_baby-panda_128x128.png)

# Advanced Topics



There are several template files (see directory `/etc/little-brother`) which can be used as a basis for 
your concrete configuration:

*   <A HREF="etc/minimal-master.config">`minimal-master.config`</A>: A minimal configuration file to run the 
    application on a single host with a simple rule set to start with.

*   <A HREF="etc/multi-rule-master.config">`multi-rule-master.config`</A>: A more elaborate configuration file 
    featuring a realistic rule set.

*   <A HREF="etc/minimal-slave.config">`minimal-slave.config`</A>: A minimal configuration file to run the 
    application on a client. This file is relatively simple since it only contains the details to connect 
    to the master host.

Choose the configuration file that best fits your needs and rename it to `little-brother.conf`. Look
at the commented entries and adapt them if required.

You will have to make at least the following adaptation:

*   Change the username in the examples to match the user(s) that you want to monitor.
*   Set a database connection parameters such as the host and optinally the port number. 

### Start the Application

Use `systemctl` to start the application:

    systemctl start little-brother
    
If `systemctl` complains about run-errors, please check the error log in `/var/log/little-brother`. 
In case no errors are returned the web interface should be available at

    http://localhost:[PORT]/
    
where `[PORT]` corresponds to the port number configured with setting  



## Client Server Mode

In addition to the master host any number of slave hosts may be configured. The assumption is that the users
to be monitored have login permission to all those hosts and that the user names on all hosts match. In this
case access times on all hosts are communicated to the master host and accumulated there. The master will
apply the rule sets and determine which users have exceeded their access times. 

A host is configured as slave by providing the `host_url` field in the `[MasterConnector]` section. 
The slaves actively contact the master. The master has no knowledge of the slaves beforehand. See below.
 
    [MasterConnector]
    host_url=http://localhost:5560
    access_token=abcdef

The field `access_token` must match the one configured on the master host. Note that for the time being the 
communication between slaves and master is always simple HTTP.

It is not required that rulesets be configured on the slaves. They will automatically distributed to all
slaves. 

## Using a Full Fledge Database  as Backend

todo: rewrite doc on database
### Create the Database

Once your configuration is complete you will have to create the database scheme. This is done by calling the application
with a specific option and passing the credentials of the database admin user:

    run_little_brother.py --config /etc/little-brother/little-brother.config --create-databases --option Persistence.database_admin=ADMINUSER Persistence.database_admin_password=PASSWORD

Note that you can also configure the credentials in the configuration file although this is not recommended since the
admin credentials are ONLY required during the creation of the database should be exposed a little as possible.


## Running Behind a Reverse Proxy

If `LittleBrother` is to be run behind a reverse proxy additional care needs to be taken if the proxy is configured
to accept the application pages at any other URL than the root url ("\"). In this case the recommended
configuration is to use the same prefix for the application itself. 

Consider the following `nginx` configuration:

    ProxyPass /LittleBrother/ http://my.local.hostname:5555/LittleBrother/
    ProxyPassReverse /LittleBrother/ http://my.local.hostname:5555/LittleBrother/

The proxy will map all pages underneath `/LittleBrother` to port `5555` of host `my.local.hostname`. 
The target of the mapping will use the same prefix `/LittleBrother`.

The `[StatusServer]` configuration section of the master host should contain the following setting:

    [StatusServer]
    ...
    proxy_prefix=/LittleBrother
    ...

## Monitoring the Application

`LittleBrother` offers two options for operational monitoring. See [here](OPERATIONAL_MONITORING.md) for details.
  
