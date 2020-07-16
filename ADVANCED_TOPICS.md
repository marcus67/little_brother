![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)

# Advanced Topics

## Detailed Configuration

Some settings of `LittleBrother`, such as the interval between checking the processes on the hosts, 
can only be set in the configuration file. The settings are described in the comments
of the configuration files. See here for templates: 

*   <A HREF="etc/master.config">`master.config`</A>: A minimal configuration file to run the 
    application on a single host.

*   <A HREF="etc/slave.config">`slave.config`</A>: A minimal configuration file to run the 
    application on a client. This file is relatively simple since it only contains the details to connect 
    to the master host.

The actual active configuration file can be found at `/etc/little-brother/little-brother.conf`.
After changes in the configuration file the application has to be restarted by issuing:

    systemctl restart little-brother

## Configuring the Web Frontend

The default URL of the web frontend is [http://localhost:5555/](http://localhost:5555/). Both the port and/or 
the relative path can be changed. Edit the appropriate settings in the configuration file:

    [StatusServer]
    port=PORT
    proxy_prefix=PREFIX

After restarting the server (see above) the web frontend can be reached at 
http://localhost:PORT/PREFIX.

## Client Server Mode

In addition to the master host any number of slave hosts may be configured. The assumption is that the users
to be monitored have login permission to all those hosts and that the user names on all hosts match. In this
case access times on all hosts are communicated to the master host and accumulated there. The master will
apply the rule sets and determine which users have exceeded their access times. 

## Users and UIDs

The default behavior of little brother is to retrieve user names and UIDs from the file `/etc/passwd` using standard
Python libraries. All users in `/etc/passwd` are eligible to be monitored which match these additional criteria:

*   the UID is between 500 and 65000,
*   the username is not `little-brother`,
*   the user has a valid password, and
*   the user's shell is neither `/usr/sbin/nologin` nor `/bin/false`.    

These restrictions should filter out all system and technical users. If you have valid users outside the UID range
above you can use the settings

    [UnixUserHandler]
    min_uid=...
    max_uid=...
    
to override the defaults.

Using `/etc/passwd`, however, may be a problem in two cases:

*   The master host does not have the users defined which will be monitored on the slaves.
*   The master host is using an LDAP server to store the users and their credentials.

In both cases you can provide the users and their respective UIDs explicitly in the configuration file:

    [UnixUserHandler]
    user_list=USERNAME1:UID1, USERNAME2:UID2, ...
 
The `USERNAME*` and `UID*` must match those on the slave hosts.

## Providing a Mapping between UIDs

When using a master-slave setup the assumption is that UIDs on the master host and the slave hosts match. In this
case no further configuration will be necessary. If however, there are differences between master and slave, it is
possible to provide a mapping of the UIDs for the user names.

<!--
TODO: Describe UID mapping feature
--> 

## Migrating From Older Revisions 

### Migrating Revisions < 41

Unfortunately, there is no support for migrating `LittleBrother` for revisions prior to 41. Please, uninstall
the software, remove the database schema, and reinstall.

### Migrating Revisions >= 41

With the introduction of `alembic` in revision 41 it has become possible to migrate the database model automatically.
The startup script of the system service has been modified in such a way that it always calls the option
`--upgrade-databases head`. 

When upgrading to a new version, after the installation of the new Debian package, you will just have to issue

    systemctl daemon-reload
    systemctl restart little-brother

### Migrating to Revision 63 (Version 0.3.x)

Between revisions 62 and 63 there have been substantial changes to the DB data model and the configuration file. 
Since the definition of the rule sets and the implicit definition of the users were moved from the 
configuration file to the database, `LittleBrother` will start an automatic migration of the data in the 
configuration file upon startup. For every subsequent run the user and rule set data in the file will be ignored.
These settings can be removed. If they are still found a warning will be issued.  

## Installation on a Slave Host

The basic installation of `LittleBrother` on a slave host is basically the same as on the master host. See the 
main [README](README.md) on how to install the Debian package. Then follow these steps:

*   Copy the slave configuration template <A HREF="etc/slave.config">`slave.config`</A> to 
`/etc/little-brother/little-brother.conf` on each slave host.

*   Choose a secret access token and set this token in the configuration on the master host:   

        [MasterConnector]
        access_token=SOME_LONG_AND_SECRET_TOKEN

*   Set the same access token in the configuration on all slave hosts. On the latter also the address of the 
master host must be set. Replace `[MASTERHOST]` by the appropriate host DNS name or IP address and
`[PORT]` by the appropriate port.

        [MasterConnector]
        host_url=http://[MASTERHOST]:[PORT]
        access_token=SOME_LONG_AND_SECRET_TOKEN

Note that for the time being the communication between slaves and master is always simple HTTP.
 
Restart the application on the slave host again by issuing

    systemctl start little-brother
    
Beside the Debian package, there is also a Docker image available which can be used on the slave host. 
See [Docker](DOCKER.md) for details.

## Using a Full Fledge Database as Backend

The default backend for `LittleBrother` is a Sqlite file oriented database. It works out of the box. If you prefer
a more mature backend you can switch to a full fledge database such as MySQL or MariaDB. This is possible, since 
the persistence uses the abstraction layer [SQLAlchemy](https://www.sqlalchemy.org/) which can be used with many 
different database systems. Currently, `LittleBrother` should work with MySQL, MariaDB and PostgreSQL.

### Configuring the Database

In order to use a database the configuration file in `/etc/little-brother/little-brother.conf` has to be adapted. 
First the SQLite backend has to be deactivated by commenting out the SQLite related setting settings and define
the settings starting with `database_`.

    [Persistence]
    #sqlite_dir = /var/spool/little-brother
    #sqlite_filename = little-brother-feature.sqlite.db
    
    database_driver = SET_ME
    database_host = SET_ME
    database_port = SET_ME
    database_admin = SET_ME
    database_name = little_brother
    database_user = little_brother
    database_password = SET_ME

Replace the `SET_ME` entries by the appropriate values. The driver and port (verify your installation!) 
must be set as follows:

| Database    | Driver Name          | Typical Port Number |
| ----------- | -------------------- | ------------------- |
| MySQL       | `mysql+pymysql`      | 3306                |
| MariaDB     | `mysql+pymysql`      | 3306                |
| PostgreSQL  | `postgresql`         | 5432                |

### Create the Database

Stop the application by issuing as root user:

    systemctl stop little-brother

Once your configuration is complete you will have to create the database scheme. This is done by calling the application
with a specific option and passing the credentials of the database admin user:

    run_little_brother.py --config /etc/little-brother/little-brother.config --create-databases --upgrade-databases --option Persistence.database_admin=ADMINUSER Persistence.database_admin_password=PASSWORD

The application will start up in non-daemon mode. Press `CTRL-C` to stop the application. If the logging shows a
successful creation of the database, start the application again by issuing as root user: 

    systemctl start little-brother

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
