![LittleBrother-Logo](little_brother/static/icons/icon-baby-panda-128x128.png)

# Change History 

This document lists all changes of `LittleBrother` with the most recent changes at the top.

## Version 0.3 Revision 63 (May/June 2020)

*   New Prometheus gauge `little_brother_configured_users`
*   Configuration for Prometheus port in test cases
*   Completely revised status handling in class `ClientDeviceHandler`
*   Use `percent` in `User2Device` to compute fractional playtime on devices
*   Closes #78, see [here](https://github.com/marcus67/little_brother/issues/78)
*   Closes #90, see [here](https://github.com/marcus67/little_brother/issues/90)
*   Closes #38, see [here](https://github.com/marcus67/little_brother/issues/38)
*   Closes #39, see [here](https://github.com/marcus67/little_brother/issues/39)
*   Closes #88, see [here](https://github.com/marcus67/little_brother/issues/88)
*   Closes #91, see [here](https://github.com/marcus67/little_brother/issues/91)
*   Provide configuration file for apparmor
*   Move creation of `/var/run/little-brother` from service configuration to tmpfiles.d configuration
*   Completely revised documentation
 
## Version 0.2.2 Revision 62 (May 6th, 2020)

*   Added Finnish localization (locale "nl")
*   Added Turkish localization (locale "tr")
*   Added Russian localization (locale "ru")
*   Added Japanese localization (locale "ja")
*   Added Bangla localization (locale "bn")
*   Added French localization (locale "fr")
*   Added Thai localization (locale "th")
*   Added two Prometheus metrics to provide version information and uptime
*   Updated Grafana dashboard 
*   Optional font scaling depending on request locale (for e.g. Bangla)
*   Closes #79, see [here](https://github.com/marcus67/little_brother/issues/79)
*   Add test cases for classes `RuleHandler` and `AppControl`
*   Closes #56, see [here](https://github.com/marcus67/little_brother/issues/56)
*   Closes #74, see [here](https://github.com/marcus67/little_brother/issues/74)
*   Closes #40, see [here](https://github.com/marcus67/little_brother/issues/40)
*   Upgrade to `python_base_app` version 0.1.9

## Version 0.2.1 Revision 61 (April 18th, 2020)

*   Closes #23, see [here](https://github.com/marcus67/little_brother/issues/23)
*   Closes #54, see [here](https://github.com/marcus67/little_brother/issues/54)
*   Closes #73, see [here](https://github.com/marcus67/little_brother/issues/73)
*   Added country flags to the README
*   Provided sample configuration for Grafana
*   Added Dutch localization (locale "nl")
*   Use completely localized date format (including day of week) for admin page
*   Show supported languages on the "About" page
*   Upgrade to `python_base_app` version 0.1.8

## Version 0.2 Revision 60 (April 13th, 2020)

*   Closes #68, see [here](https://github.com/marcus67/little_brother/issues/68)
*   Closes #69, see [here](https://github.com/marcus67/little_brother/issues/69)
*   Remove some Codacy warnings

## Version 0.2 Revision 59 (April 12th, 2020)

*   Export locale and current notification message for use in LittleBrotherTaskbar
*   Supply missing Italian translations and correct some variable references in them 

## Version 0.2 Revision 58 (April 12th, 2020)

*   Moved helper classes for audio handling from LittleBrother to python_base_app

## Version 0.2 Revision 57 (April 11th, 2020)

*   Mention new `LittleBrotherTaskbar` in `README.md`
*   Remove `python-base-app` from `requirements.txt`

## Version 0.2 Revision 56 (April 8th, 2020)

*   Upgrade to new `python_base_app`
*   Dynamically generate `install_requires` in `setup.py`

## Version 0.2 Revision 55 (April 1st, 2020)

*   Move taskbar app into a [repository](https://github.com/marcus67/little_brother_taskbar) of its own
*   Split setup configuration into standard and extended settings 
*   Remove superfluous entries in MANIFEST.in

## Version 0.2 Revision 54 (March 24th, 2020)

*   Remove speech engine support for `pyttsx3` due to [issue 67](https://github.com/marcus67/little_brother/issues/67)
*   Fixes #67
*   Remove audio player support for `playsound` due to persisting issues with import of module `gi` 
*   Add taskbar app (see [issue 66](https://github.com/marcus67/little_brother/issues/66))
*   Update calendar handler for German school vacation to API version 2.0

## Version 0.2 Revision 53 (March 7th, 2020)

*   Move alembic files into package directory to make them available in the pip installation directory
*   Add command line option '--stamp-databases' to force an alembic database revision  
*   Correct alembic.sh (invalid use of env variable)
*   Correct German translation
*   Exclude alembic delta scripts from duplicate checks (after move of directory)

## Version 0.2 Revision 52 (March 4th, 2020)

*   Add troubleshooting page. 

## Version 0.2 Revision 51 (February 26th, 2020)

*   Upgrade PIP package `codecov` to version 2.0.16 due to 
    [CVE-2019-10800](https://snyk.io/vuln/SNYK-PYTHON-CODECOV-552149) 

## Version 0.2 Revision 50 (January 3rd, 2020)

*   Try both paths `/usr/bin/pip3` and `/usr/local/bin/pip3` during Debian package post installation
*   Install PIP package `setuptools` during Debian package post installation 
*   Add `python-dev` and `python3-dev` to Debian dependencies

## Version 0.2 Revision 49 (January 1st, 2020)

*   Remove some coding warnings
*   Add test cases for class ClientDeviceHandler
*   Add specific versions to apt-get packages in Dockerfile

## Version 0.1 Revision 48 (December 26th, 2019)

*   Added Docker image for slave process
*   Support for overriding of settings using environment
*   Abstraction of the audio engine (class `BaseAudioPlayer`)
*   Support for `mpg123` as audio engine (new)
*   Support for `playsound` as audio engine (rewritten as engine)
*   Support for `pyglet` as audio engine (new)
*   Correct handling of default locale on slave device
*   Distribution of login mappings from master to slave (for Docker containers and MacOS)
*   New CI stage to build docker images
*   Consistent hiding of sensitive variable values in logging
*   Packages `sudo` and `procps` added to the Debian package dependencies
*   Explicit call of `pip3` using absolute path in Debian control file 
*   Closes #53, see [here](https://github.com/marcus67/little_brother/issues/53)
*   Provide simple shell script to grant message clients access to X server
*   Several test cases added

## Version 0.1 Revision 47 (October 26th, 2019)

*   Fixed problem with generated kill command under Linux
*   Fixed several issues reported by Codacy
*   Turned CI status into a table (including MacOS branch)

## Version 0.1 Revision 46 (October 25th, 2019)

*   Generate script for building Docker images
*   Add list typed option values to configuration files
*   Improve test coverage of Configuration.py
*   Provide initial Docker images for little-brother servers (non functional)

## Version 0.1 Revision 45 (October 21st, 2019)

*   Closes #60, see [here](https://github.com/marcus67/little_brother/issues/60)
*   Make ProcessControl an abstract base class
*   Use launchctl to terminate login process under MacOs
*   Remove duplicate PopupHandler section in minimal-master.config
*   Switch to effective user id in process infos
*   Add missing -SIGHUP for MacOs kill command
*   Use ConfigurationException

## Version 0.1 Revision 44 (October 9th, 2019)

*   Closes #30, see [here](https://github.com/marcus67/little_brother/issues/30)
*   Closes #4, see [here](https://github.com/marcus67/little_brother/issues/4)
*   Increased default value for DEFAULT_MINIMUM_DOWNTIME_DURATION to 20
*   Improved exception handling upon startup
*   Improved security of Popen by using shlex

## Version 0.1 Revision 43 (October 5th, 2019)

*   Closes #8 again, see [here](https://github.com/marcus67/little_brother/issues/8) after actually considering
    downtimes in statistics

*   Fix some minor code quality problems reported by Codacy 

*   Added output of downtime values to status page using font color yellow.

*   Increase test coverage for popup_handler.py and rule_handler.py

## Version 0.1 Revision 42 (October 5th, 2019)

*   Closes #8, see [here](https://github.com/marcus67/little_brother/issues/8)
*   Fix some minor code quality problems reported by Codacy 
*   Provide special builtin methods to RecurringTask to eliminate tuple handling

## Version 0.1 Revision 41 (June 20th, 2019)

*   Closes #7, see [here](https://github.com/marcus67/little_brother/issues/7) 
    (has actually already been taken care of in previous commits)

*   Closes #16, see [here](https://github.com/marcus67/little_brother/issues/16)

*   Introduce alembic for database initialization and migration

## Version 0.1 Revision 40 (June 9th, 2019)

*   Actually committed the Italian localization (files were missing, mea culpa) 
*   Corrected name of fourth popup tool in sample configuration files
*   Added YouTube presentation

## Version 0.1 Revision 39 (June 5th, 2019)

*   [Albano Battistella](https://github.com/albanobattistella) provided the Italian translation. Thanks! 
*   Fixed some typos in the README file.

## Version 0.1 Revision 38 (June 2nd, 2019)

*   Small changes in README.md and sample configuration file reflecting test installation 
    from scratch on Ubuntu 18.10.

## Version 0.1 Revision 37 (May 29th, 2019)

*   Prepare pybabel files for Italian

## Version 0.1 Revision 36 (May 29th, 2019)

*   Closes #51, see [here](https://github.com/marcus67/little_brother/issues/51)
*   Change defaults for database driver (to match pre-loaded PIP package for mysql)

## Version 0.1 Revision 35 (June 1st, 2019)

*   Closes #9, see [here](https://github.com/marcus67/little_brother/issues/9)
*   Closes #50, see [here](https://github.com/marcus67/little_brother/issues/50)
*   Improve test coverage.

## Version 0.1 Revision 34 (May 26th, 2019)

*   Closes #13, see [here](https://github.com/marcus67/little_brother/issues/13)
*   Improve test coverage.
*   Choose better colors grades for nested rows in admin and index pages

## Version 0.1 Revision 33 (May 11th, 2019)

*   Boost test coverage.
*   Several changes proposed by codacy.
*   Add `post_process` to class `configuration.ConfigModel`

## Version 0.1 Revision 32 (May 9th, 2019)

*   Several changes proposed by codacy.

## Version 0.1 Revision 31 (May 8th, 2019)

*   Closes #44, see [here](https://github.com/marcus67/little_brother/issues/44)
*   Add hyperlink to [Facebook page](https://www.facebook.com/littlebrotherdebian/)

## Version 0.1 Revision 30 (May 4th, 2019)

*   Closes #15, see [here](https://github.com/marcus67/little_brother/issues/15)
*   Several changes proposed by codacy.

## Version 0.1 Revision 29 (May 4th, 2019)

*   Closes #5, see [here](https://github.com/marcus67/little_brother/issues/5)
*   Closes #10, see [here](https://github.com/marcus67/little_brother/issues/10)
*   Closes #14, see [here](https://github.com/marcus67/little_brother/issues/10)
*   Round remaining play times to nearest minute in notifications.
*   Instantiate flask_wtf.FlaskForm instead of flask_wtf.Form (obsolete).
*   Several changes proposed by codacy.
  
## Version 0.1 Revision 28 (May 2nd, 2019)

*   Add code quality badge by codacy to README.md.
*   Make first improvements to code found by codacy.

## Version 0.1 Revision 27 (May 1st, 2019)

*   Closes #17, see [here](https://github.com/marcus67/little_brother/issues/17)
*   Closes #18, see [here](https://github.com/marcus67/little_brother/issues/18)
*   Closes #35, see [here](https://github.com/marcus67/little_brother/issues/35)
*   Closes #36, see [here](https://github.com/marcus67/little_brother/issues/36)
*   Improve test coverage of process_statistics.py.
*   Include requirement.txt to be scanned by snyk.io.

## Version 0.1 Revision 26 (April 29th, 2019)

*   Closes #6 (again), see [here](https://github.com/marcus67/little_brother/issues/6)
*   Closes #11, see [here](https://github.com/marcus67/little_brother/issues/11)

## Version 0.1 Revision 25 (April 27th, 2019)

*   Closes #6, see [here](https://github.com/marcus67/little_brother/issues/6)

## Version 0.1 Revision 24 (April 22nd, 2019)

*   Added first version of ARCHITECTURE.md.

## Version 0.1 Revision 23 (April 22nd, 2019)

*   Add screenshots to README.md.
*   Move "under construction" logo to `doc`.

## Version 0.1 Revision 22 (April 21st, 2019)

*   Add download logo to README.md.
*   Link both directories `release` and `master` at SourceForge.

## Version 0.1 Revision 21 (April 21st, 2019)

*   Add coverage logo to README.md. 
*   Add this CHANGES.md page.
*   Interpret predefined environment variables (e.g. CIRCLE_BRANCH).
*   Expand environment variables before calling scripts.
