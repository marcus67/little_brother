# API Description

## Overview

This page describes how the LittleBrother server interacts with the LittleBrother client and the desktop app 
LittleBrotherDesktop.

<img alt="API Overview" src="doc/application-api.drawio.png">

## Client to Server Communication

All communication between the client and the server is initiated by the client. It regularly sends messages to the 
server using the REST API of the server.

Each message from the client to the server has the attributes `secret`, `hostname`, an array of administration events
(class [`AdminEvent`](#administration-event)), and one instance of the class [`ClientStats`](#client-statistics). 

The server answers by sending 0 to n admin events back. 
See [Server to Client Communication](#server-to-client-responses).

### Standard Client to Server Message Without Events

The array of admin events can be empty, so the simplest message is as follows.

TODO: Replace values by typical Linux ones.

    {
      'secret': 'abcdef',
      'hostname': 'beethoven',
      'events': [],
      'client_stats': {
        'cpu_seconds_total': 0.0,
        'linux_distribution': 'Darwin 23.5.0',
        'python_version': '3.11.9',
        'resident_memory_bytes': 0.0,
        'revision': '200',
        'running_in_docker': False,
        'running_in_snap': False,
        'start_time_seconds': 0.0,
        'version': '0.5.1'
      }
    }

### Standard Client to Server Message With Events

The following example contains one instance of the `AdminEvent` (see [below](#administration-event)):

    {
      'secret': 'abcdef',
      'hostname': 'beethoven',
      'events': [
        {
          'delay': 0,
          'downtime': 0,
          'event_time': '2024-07-16 15:11:24',
          'event_type': 'PROCESS_START',
          'hostlabel': None,
          'hostname': 'beethoven',
          'locale': None,
          'payload': None,
          'percent': 100,
          'pid': 88176,
          'process_start_time': '2024-07-16 15:10:08',
          'processhandler': 'ClientProcessHandler',
          'processname': None,
          'text': None,
          'username': 'amelie'
        }
      ],
      'client_stats': {
        'cpu_seconds_total': 0.0,
        'linux_distribution': 'Darwin 23.5.0',
        'python_version': '3.11.9',
        'resident_memory_bytes': 0.0,
        'revision': '200',
        'running_in_docker': False,
        'running_in_snap': False,
        'start_time_seconds': 0.0,
        'version': '0.5.1'
      }
    }

### Administration Event

The administration event is modeled by class [AdminEvent](little_brother/admin_event.py). The event is used for 
a variety of purposes and hence comprises a union of attributes only some of which are filled for a specific purpose. 

| Attribute            | Description                                                                                                                                                                                                                                                                                                                              |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| `hostname`           | Name of the host that this event is coming FROM.                                                                                                                                                                                                                                                                                         |
| `username`           | Name (login) of the user that event is related to, None if the event is not user-related.                                                                                                                                                                                                                                                |
| `pid`                | PID (process id) of the process at operating system level (e.g. as returned by "ps") that the event is related to, None if the event is not user-process-related.                                                                                                                                                                        |
| `processhandler`     | Class name of the instance handling the process events. For the processes which are monitored by "ps" this will always be "ClientProcessHandler", None if the event is not user-process-related.                                                                                                                                         |
| `processname`        | Name of the process that the event is related to in event type PROCESS_START, None if the event is not user-process-related or the type is PROCESS_END.                                                                                                                                                                                  |
| `event_type`         | Name of the event type. See [here](#event-types) for a list of types                                                                                                                                                                                                                                                                     |
| `event_time`         | Timestamp of the creation of this event instance in the format "2024-07-17 18:37:44"                                                                                                                                                                                                                                                     |
| `process_start_time` | Timestamp of the creation of the user process that the event is related to (as reported by "ps") in format "2024-07-17 18:37:44", None if the event is not user-process-related. Note: This timestamp will be used in combination with p_pid to derive a unique id of the process since the pid by itself may be recycled after a while! |
| `text`               | TODO                                                                                                                                                                                                                                                                                                                                     |
| `locale`             | TODO                                                                                                                                                                                                                                                                                                                                     |
| `payload`            | Additional structured data used in some of the events types.                                                                                                                                                                                                                                                                             |
| `downtime`           | Downtime in seconds during the runtime of the given process id.                                                                                                                                                                                                                                                                          |
| `percent`            | Only used in connection with the class "ClientDeviceHandler" when the activity of a used is derived from "pinging" hosts: Percentage of the time used as activity of the user.                                                                                                                                                           |
| `hostlabel`          | Only used in connection with the class "ClientDeviceHandler" when the activity of a used is derived from "pinging" hosts: Label of the host on which the user activity occurred.                                                                                                                                                         |
| `delay`              | Delay in seconds before the client should terminate a process in an event of type `KILL_PROCESS`.                                                                                                                                                                                                                                        |

### Event Types

The following table shows all available event types. The types are specific for the direction of the communication.
See column *Minimal* for the combination of events which need to be implemented on the client side to provide a minimal
client functionality.

| Type                                                       | Direction     | Minimal | Description                                                                                                                               |
|------------------------------------------------------------|---------------|---------|-------------------------------------------------------------------------------------------------------------------------------------------|
| [`PROCESS_START`](#event-type-process_start)               | both          | *       | Announce that a new/historic process matching the pattern `Login Process Name Pattern` (in the user configuration dialog) has been found. |
| [`PROHIBITED_PROCESS`](#event-type-prohibited_process)     | client2server |         | Announce that a new process matching the pattern `Prohibited Process Name Pattern` (in the user configuration dialog) has been found.     |
| [`PROCESS_END`](#event-type-process_end)                   | client2server | *       | Announce that a process (which had been announced previously using `PROCESS_START` or `PROHIBITED_PROCESS` has terminated.                |
| [`PROCESS_DOWNTIME`](#event-type-process_downtime)         | client2server |         | Announce that the client has had some downtime (e.g. it had been put into hibernation mode and as just recovered from it).                |
| [`START_CLIENT`](#event-type-start_client)                 | client2server |         | Announce to the server that a client is (re-)starting.                                                                                    |
| [`START_MASTER`](#event-type-start_master)                 | server2client |         | This event is sent to all new clients exactly once after sending their first message to the server.                                       |
| [`KILL_PROCESS`](#event-type-kill_process)                 | server2client | *       | Prompt the client to kill a specific process given by its PID.                                                                            |
| [`UPDATE_CONFIG`](#event-type-update_config)               | server2client | *       | Communicate to the client that the configuration has changed.                                                                             |
| [`UPDATE_LOGIN_MAPPING`](#event-type-update_login_mapping) | server2client | *       | Communicate to the client that login mapping has changed.                                                                                 |

[UPDATE_LOGIN_MAPPING](#event-type-update_login_mapping)

#### Event Type `PROCESS_START`

This event announces that a new process matching the pattern `Login Process Name Pattern` (in the user configuration 
dialog) has been found. Ideally, this event is only sent once. However, the server is able to handle multiple instances
of the same event in a benign fashion. The event will definitely be resent, when the client needed to be restarted.

When the process is terminated at a later point of time, the client will issue an associated `PROCESS_END` event.

    {
      "delay": 0,
      "downtime": 0,
      "event_time": "2024-07-18 13:40:22",
      "event_type": "PROCESS_START",
      "hostlabel": null,
      "hostname": "beethoven",
      "locale": null,
      "payload": null,
      "percent": 100,
      "pid": 85240,
      "process_start_time": "2024-07-18 13:40:22",
      "processhandler": "ClientProcessHandler",
      "processname": "zsh",
      "text": null,
      "username": "amelie"
    }

##### Server to Client Variant

When the client is shutdown cleanly it does not have a chance to inform the server about the status of the user 
processes, so the server might end up with entries of active user processes on the client which do not exist anymore.
Since the client does not have any entries it will never send `PROCESS_END` events for them. To correct this, the 
server will send `PROCESS_START` events to the client of all user processes that were active when the client died. The
client will receive them and check the existence of the user processes. If the processes are still active nothing will
happen and status on server and client are synchronized again. If the user processes are not active anymore, the client
will send regular `PROCESS_END` events also synchronizing the status.

The typical content of the event is the same as in the opposite direction. See above for an example.

#### Event Type `PROHIBITED_PROCESS`

This event announces that a new process matching the pattern `Prohibited Process Name Pattern` (in the user 
configuration dialog) has been found. Note: This event will be sent over and over again until the prohibited process 
has been terminated.

    {
      "delay": 0,
      "downtime": 0,
      "event_time": "2024-07-18 13:11:08",
      "event_type": "PROHIBITED_PROCESS",
      "hostlabel": null,
      "hostname": "beethoven",
      "locale": null,
      "payload": null,
      "percent": 100,
      "pid": 83544,
      "process_start_time": "2024-07-18 13:11:03",
      "processhandler": "ClientProcessHandler",
      "processname": "tail",
      "text": null,
      "username": "amelie"
    }

#### Event Type `PROCESS_END`

This event announces that a process (which had been announced previously using `PROCESS_START`) has terminated. The
primary key of the process is a combination of the attributes `pid` and `process_start_time`.
Ideally, this event is only sent once for each terminated process. However, the server is able to accept multiple
instances of the same event in a benign fashion. Superfluous events will simply be ignored.

    {
      "delay": 0,
      "downtime": 0,
      "event_time": "2024-07-18 13:28:05",
      "event_type": "PROCESS_END",
      "hostlabel": null,
      "hostname": "beethoven",
      "locale": null,
      "payload": null,
      "percent": 100,
      "pid": 83507,
      "process_start_time": "2024-07-18 13:10:32",
      "processhandler": "ClientProcessHandler",
      "processname": null,
      "text": null,
      "username": "amelie"
    }

In case the client is shut down in a controlled way, it will also send this event for ALL active processes no matter
if they have (been) terminated or not. This is based on the assumption that the shutdown of the client was triggered 
by shutdown of the client host, so that the user processes would be terminated anyway. If the latter is not case and the
client is restarted it will resend the `PROCESS_START` events.

Note that prohibited processes (announced by `PROHIBITED_PROCESS`) will not trigger a `PROCESS_END` 
when they terminated. In this case the client will just stop sending `PROHIBITED_PROCESS` events.

#### Event Type `PROCESS_DOWNTIME`

This event announces that the client has had some downtime (e.g. it had been put into hibernation mode and 
as just recovered from it). Note that this event always refers to a concrete process id which has previously been 
announced using `PROCESS_START`. It uses the same primary key from `pid` and `process_start_time` as the 
`PROCESS_START` event. The information of a downtime will be used to correct the effective login time of a user. 
The accumulated downtime will be shown in the [Status View](WEB_FRONTEND_MANUAL.md#listing-the-status). 

    {
      "delay": 0,
      "downtime": 72,
      "event_time": "2024-07-18 13:43:01",
      "event_type": "PROCESS_DOWNTIME",
      "hostlabel": null,
      "hostname": "beethoven",
      "locale": null,
      "payload": null,
      "percent": 100,
      "pid": 85240,
      "process_start_time": "2024-07-18 13:40:22",
      "processhandler": "ClientProcessHandler",
      "processname": null,
      "text": null,
      "username": "amelie"
    }

#### Event Type `START_CLIENT`

This event announces to the server that a client is (re-)starting. This will trigger the server to resend the 
configuration and login mappings. See `UPDATE_CONFIG` and `UPDATE_LOGIN_MAPPING` events. 

    {
      "delay": 0,
      "downtime": 0,
      "event_time": "2024-07-18 13:46:25",
      "event_type": "START_CLIENT",
      "hostlabel": null,
      "hostname": "beethoven",
      "locale": null,
      "payload": null,
      "percent": 100,
      "pid": null,
      "process_start_time": null,
      "processhandler": null,
      "processname": null,
      "text": null,
      "username": null
    }

#### Event Type `START_MASTER`

This event is sent to all clients exactly when the server is (re-)started. This will trigger all clients to send
their active processes using `PROCESS_START` events. This ensures that after the master has come up it will have a 
comprehensive view of all active user processes on the clients.

    {
        "delay": 0,
        "downtime": 0,
        "event_time": "2024-07-18 13:39:49",
        "event_type": "START_MASTER",
        "hostlabel": null,
        "hostname": "beethoven",
        "locale": null,
        "payload": null,
        "percent": 100,
        "pid": null,
        "process_start_time": null,
        "processhandler": null,
        "processname": null,
        "text": null,
        "username": null
    }

#### Event Type `KILL_PROCESS`

This event prompts the client to kill a specific process given by its PID and its start time. The client will usually
react by killing exactly the process given by its `pid` and `process_start_time` but the active process handler may
have other strategies. On the Mac, for example, it will try to log out the user using a completely different binary.
The event has a `delay` time which the client is supposed to wait before it actually kills the process. This ensures 
that audio messages can still be output to the user using the LittleBrother desktop utility.

    {
        "delay": 0,
        "downtime": 0,
        "event_time": "2024-07-18 13:59:37",
        "event_type": "KILL_PROCESS",
        "hostlabel": null,
        "hostname": "beethoven",
        "locale": null,
        "payload": null,
        "percent": 100,
        "pid": 86205,
        "process_start_time": "2024-07-18 13:59:29",
        "processhandler": "ClientProcessHandler",
        "processname": null,
        "text": null,
        "username": "amelie"
    }


#### Event Type `UPDATE_CONFIG`

This event communicates to the client that the configuration has changed. It uses the attribute `payload` to transfer
the updated configuration as a dictionary. Currently, there are two keys:

* `config:user_config`: Contains a dictionary of user settings for each monitored user with the user login as the key 
    of the dictionary.
* `config:config:maximum_time_without_send`: Contains the maximum number of seconds that clients will tolerate
    a missing connection to the server. 
    See [Network Tempering Detection](ADVANCED_TOPICS.md#network-tempering-detection).


    {
        "delay": 0,
        "downtime": 0,
        "event_time": "2024-07-18 13:39:49",
        "event_type": "UPDATE_CONFIG",
        "hostlabel": null,
        "hostname": "beethoven",
        "locale": null,
        "payload": {
          "config:user_config": {
            "leon": {
              "process_name_pattern": "systemd|bash|sh|csh|tsh",
              "prohibited_process_name_pattern": "",
              "active": true
            },
            "christoph": {
              "process_name_pattern": "systemd|bash|sh|csh|tsh",
              "prohibited_process_name_pattern": "",
              "active": true
            },
            "amelie": {
              "process_name_pattern": "systemd|bash|sh|csh|tsh|zsh|sshd*",
              "prohibited_process_name_pattern": "tail",
              "active": true
            }
          },
          "config:maximum_time_without_send": 50
        },
        "percent": 100,
        "pid": null,
        "process_start_time": null,
        "processhandler": null,
        "processname": null,
        "text": null,
        "username": null
    }


#### Event Type `UPDATE_LOGIN_MAPPING`

This event communicates to the client that the login mapping has changed. It uses the attribute `payload` to transfer
the mapping consisting of an array of server group entries.  Each server group, again, contains an array of
`LoginUidMappingEntry` tuples.

    {
        "delay": 0,
        "downtime": 0,
        "event_time": "2024-07-18 13:39:49",
        "event_type": "UPDATE_LOGIN_MAPPING",
        "hostlabel": null,
        "hostname": "beethoven",
        "locale": null,
        "payload": [
          [
            "mac",
            [
              [
                "amelie",
                503
              ],
              [
                "mr",
                505
              ]
            ]
          ]
        ],
        "percent": 100,
        "pid": null,
        "process_start_time": null,
        "processhandler": null,
        "processname": null,
        "text": null,
        "username": null
    }


### Client Statistics

The client statistics are modeled by class [ClientStats](little_brother/client_stats.py). On Linux systems most of
the attributes are retrieved using the packages `sys`, `distro`, and `prometheus_client`. For details see method
`get_client_stats` in [AppControl](little_brother/app_control.py). The server stores the latest versions of the 
statistics for each client and uses them to show the
[Topology Overview](WEB_FRONTEND_MANUAL.md#checking-the-topology-of-the-littlebrother-network-).

| Attribute               | Description                                                                                        |
|-------------------------|----------------------------------------------------------------------------------------------------|
| `version`               | Version of the LittleBrother application.                                                          |
| `revision`              | Debian package revision of the LittleBrother package.                                              |
| `python_version`        | Version of the Python interpreter running LittleBrother.                                           |
| `running_in_docker`     | `true`, if the application is running inside a Docker container, `false` otherwise.                |
| `running_in_snap`       | `true`, if the application is running inside a Snap container, `false` otherwise.                  |
| `linux_distribution`    | Version of the distribution of Linux (or other operating System) that LittleBrother is running on. |
| `resident_memory_bytes` | Number of bytes that LittleBrother is currently allocating (as e.g. reported by ``on Linux).       |
| `start_time_seconds`    | Start time of LittleBrother on the client in seconds since EPOCH.                                  |
| `cpu_seconds_total`     | Number of CPU seconds used since the start of the client.                                          |

## Server to Client Responses

Messages which are returned to the calling client consist of an array of administration events which will (as a rule)
be empty. So, the most common response will be:

    []

The most common non-empty answer of the server is to request the killing of one or more processes:

    [
      {
        "delay": 10,
        "downtime": 0,
        "event_time": "2024-07-17 18:40:09",
        "event_type": "KILL_PROCESS",
        "hostlabel": null,
        "hostname": "beethoven",
        "locale": null,
        "payload": null,
        "percent": 100,
        "pid": 41350,
        "process_start_time": "2024-07-17 18:37:43",
        "processhandler": "ClientProcessHandler",
        "processname": null,
        "text": null,
        "username": "amelie"
      }
    ]

For some events the `payload` field will contain some additional structured information, such as an updated 
configuration for the event type `UPDATE_CONFIG`:

    [
      {
        "delay": 0,
        "downtime": 0,
        "event_time": "2024-07-17 18:56:44",
        "event_type": "UPDATE_CONFIG",
        "hostlabel": null,
        "hostname": "beethoven",
        "locale": null,
        "payload": {
          "config:user_config": {
            "leon": {
              "process_name_pattern": "systemd|bash|sh|csh|tsh",
              "prohibited_process_name_pattern": "",
              "active": true
            },
            "christoph": {
              "process_name_pattern": "systemd|bash|sh|csh|tsh",
              "prohibited_process_name_pattern": "",
              "active": true
            },
            "amelie": {
              "process_name_pattern": "systemd|bash|sh|csh|tsh|zsh|sshd*",
              "prohibited_process_name_pattern": "",
              "active": true
            }
          },
          "config:maximum_time_without_send": 50
        },
        "percent": 100,
        "pid": null,
        "process_start_time": null,
        "processhandler": null,
        "processname": null,
        "text": null,
        "username": null
      }
    ]

## Providing Support for Other Operating Systems

The main process detection functionality resides in 
class [ClientProcesshandler](little_brother/client_process_handler.py) which was mainly written with Linux in mind. It
has one specific adaption to macOS when it comes to terminating a user session: it uses `/bin/launchctl bootout` 
instead of `/bin/kill` to terminate a user session.

Additional support for other operating systems will probably have to make specific changes in that class or define 
a base class which can be implemented for each operating system.

## Communication Between Server and Desktop App

TODO
