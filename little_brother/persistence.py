# -*- coding: utf-8 -*-

# Copyright (C) 2019-2021  Marcus Rickert
#
# See https://github.com/marcus67/little_brother
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import datetime
import os.path
import urllib.parse

import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy.exc import ProgrammingError

from little_brother import constants
from little_brother import persistence_base
from little_brother import persistent_admin_event
from little_brother import persistent_device
from little_brother import persistent_process_info
from little_brother import persistent_rule_override
from little_brother import persistent_user
from little_brother import persistent_user_2_device
from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

SECTION_NAME = "Persistence"


def _(x):
    return x


def copy_attributes(p_from, p_to, p_only_existing=False):
    for (key, value) in p_from.__dict__.items():
        if not key.startswith('_'):
            if key in p_to.__dict__ or not p_only_existing:
                setattr(p_to, key, value)


def create_class_instance(p_class, p_initial_values):
    instance = p_class()
    copy_attributes(p_from=p_initial_values, p_to=instance)
    return instance


class PersistenceConfigModel(configuration.ConfigModel):

    def __init__(self):
        super(PersistenceConfigModel, self).__init__(SECTION_NAME)
        self.database_driver = 'mysql+pymysql'
        self.database_host = 'localhost'
        self.database_port = 3306
        self.database_name = 'little_brother'
        self.database_user = None
        self.database_password = None
        self.database_admin = None
        self.database_admin_password = None

        self.sqlite_dir = None
        self.sqlite_filename = "little-brother.sqlite.db"

        #: Number of seconds that a database connection will be kept in the pool before it is discarded.
        #: It has to be shorter than the maximum time that a database server will keep a connection alive.
        #: In case of MySql this will be eight hours.
        #: See https://stackoverflow.com/questions/6471549/avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server
        #: Default value: :data:``
        self.pool_recycle = 3600

        self.pool_size = 10
        self.max_overflow = 20


class SessionContext(object):
    _session_registry = []

    def __init__(self, p_persistence, p_register=False):

        self._persistence = p_persistence
        self._session = None
        self._caches = {}

        if p_register:
            SessionContext._session_registry.append(self)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_session()
        return True

    def get_cache(self, p_name):

        # result =
        # print(str(self) + " get_cache " + p_name + " " + str(result if result is not None else "NONE"))
        return self._caches.get(p_name)

    def clear_cache(self):

        # print(str(self) + "clear_cache " + str(self._caches))

        #        if self._session is not None:
        #            self._session.close()
        #            self._session = None

        self._caches = {}

    def get_session(self):

        if self._session is None:
            self._session = self._persistence.get_session()

        return self._session

    def close_session(self):
        if self._session is not None:
            self._session.close()
            self._session = None

    def set_cache(self, p_name, p_object):

        # print(str(self) + " set_cache " + p_name + " " + str(p_object))

        if self._persistence.enable_caching():
            self._caches[p_name] = p_object

    @classmethod
    def clear_caches(cls):

        for context in cls._session_registry:
            context.clear_cache()


class Persistence(object):

    def __init__(self, p_config, p_reuse_session=True):

        self._logger = log_handling.get_logger(self.__class__.__name__)
        self._config = p_config
        self._session_used = False
        self._admin_session = None
        self._create_table_session = None
        self._admin_engine = None
        self._create_table_engine = None
        self._reuse_session = p_reuse_session
        self._devices = None
        self._users_session = None
        self._devices_session = None
        self._cache_entities = True

        if self._config.database_user is not None:
            tools.check_config_value(p_config=self._config, p_config_attribute_name="database_password")

        if self._config.database_admin is not None and self._config.database_admin_password is not None:

            url = urllib.parse.urlunsplit(
                (
                    self._config.database_driver,
                    "%s:%s@%s:%d" % (
                        self._config.database_admin, self._config.database_admin_password,
                        self._config.database_host, self._config.database_port),
                    '',
                    None,
                    None
                ))

            fmt = "Database URL for administrative access: '%s'" % tools.anonymize_url(url)
            self._logger.info(fmt)

            if persistence_base.DATABASE_DRIVER_POSTGRESQL in self._config.database_driver:
                isolation_level = 'AUTOCOMMIT'

            else:
                isolation_level = None

            if isolation_level is not None:
                self._create_table_engine = sqlalchemy.create_engine(url, isolation_level=isolation_level)

            else:
                self._create_table_engine = sqlalchemy.create_engine(url)

            self._admin_engine = sqlalchemy.create_engine(url, pool_recycle=self._config.pool_recycle)

        url = self.build_url()

        fmt = "Database URL for normal access: '%s'" % tools.anonymize_url(url)
        self._logger.info(fmt)

        options = {'pool_recycle': self._config.pool_recycle}

        if (persistence_base.DATABASE_DRIVER_POSTGRESQL in self._config.database_driver or
                persistence_base.DATABASE_DRIVER_MYSQL in self._config.database_driver):
            options['pool_size'] = self._config.pool_size
            options['max_overflow'] = self._config.max_overflow

        # if DATABASE_DRIVER_SQLITE in self._config.database_driver:
        #     options['check_same_thread'] = False

        self._engine = sqlalchemy.create_engine(url, **options)

    def build_url(self):

        if self._config.database_driver != persistence_base.DATABASE_DRIVER_SQLITE:
            if self._config.database_user is None:
                raise configuration.ConfigurationException("No database user configured!")

            url = urllib.parse.urlunsplit(
                (
                    self._config.database_driver,
                    "%s:%s@%s:%d" % (
                        self._config.database_user, self._config.database_password,
                        self._config.database_host, self._config.database_port),
                    self._config.database_name,
                    None,
                    None
                ))
        else:
            if self._config.sqlite_dir is None:
                url = "{driver}://".format(driver=self._config.database_driver)

            else:
                sqlite_filename = os.path.join(self._config.sqlite_dir, self._config.sqlite_filename)
                url = "{driver}:///{filename}".format(driver=self._config.database_driver, filename=sqlite_filename)

        return url

    def get_admin_session(self):
        if self._admin_session is None:
            fmt = "Open database for administrative access"
            self._logger.info(fmt)
            self._admin_session = sqlalchemy.orm.sessionmaker(bind=self._admin_engine)()
        return self._admin_session

    def get_create_table_session(self):
        if self._create_table_session is None:
            fmt = "Open database for CREATE TABLE"
            self._logger.info(fmt)
            self._create_table_session = sqlalchemy.orm.sessionmaker(bind=self._create_table_engine)()
        return self._create_table_session

    def get_connection(self):
        return self._engine.connect()

    def enable_caching(self):
        # SQLite has some restrictions with persistent entities used in threads other that the one they
        # were created in so we turn out caching.
        return persistence_base.DATABASE_DRIVER_SQLITE not in self._config.database_driver

    def get_session(self):
        if not self._session_used:
            fmt = "Open database for normal access"
            self._logger.info(fmt)
            self._session_used = True

        return sqlalchemy.orm.scoped_session(sqlalchemy.orm.sessionmaker(bind=self._engine))()

    def create_mysql(self, p_create_tables):

        if not self.check_create_table_engine():
            return

        fmt = "Creating database '%s'" % self._config.database_name
        self._logger.info(fmt)

        try:
            self._create_table_engine.execute(
                "CREATE DATABASE %s DEFAULT CHARACTER SET utf8 DEFAULT COLLATE utf8_general_ci;" % (
                    self._config.database_name))

        except ProgrammingError:
            fmt = "Database '%s' already exists" % self._config.database_name
            self._logger.info(fmt)
            return

        fmt = "Creating user '%s'" % self._config.database_user
        self._logger.info(fmt)

        try:
            self._admin_engine.execute("CREATE USER '%s' IDENTIFIED BY '%s';" % (
                self._config.database_user,
                self._config.database_password))

        except ProgrammingError:
            fmt = "User '%s' already exists" % self._config.database_user
            self._logger.info(fmt)

        fmt = "Granting access to user '%s'" % self._config.database_user
        self._logger.info(fmt)

        try:
            self._admin_engine.execute("GRANT ALL ON %s.* to '%s';" % (
                self._config.database_name,
                self._config.database_user))

        except ProgrammingError:
            fmt = "Access already granted"
            self._logger.info(fmt)

        if p_create_tables:
            persistence_base.Base.metadata.create_all(self._engine)

    def init_mysql(self):
        pass

    def create_postgresql(self, p_create_tables):

        if not self.check_create_table_engine():
            return

        fmt = "Creating user '%s'" % self._config.database_user
        self._logger.info(fmt)

        try:
            sql = "CREATE USER {db_user} WITH PASSWORD '{password}';"
            self._admin_engine.execute(
                sql.format(db_user=self._config.database_user, password=self._config.database_password))

        except ProgrammingError:
            fmt = "User '%s' already exists" % self._config.database_user
            self._logger.info(fmt)

        fmt = "Creating database '%s'" % self._config.database_name
        self._logger.info(fmt)

        try:
            # noinspection SqlInjection
            sql = "CREATE DATABASE {db_name} WITH OWNER = {db_user} ENCODING = 'UTF8';"
            self._create_table_engine.execute(
                sql.format(db_name=self._config.database_name, db_user=self._config.database_user))

        except ProgrammingError:
            fmt = "Database '%s' already exists" % self._config.database_name
            self._logger.info(fmt)
            return

        if p_create_tables:
            persistence_base.Base.metadata.create_all(self._engine)

    def create_sqlite(self, p_create_tables):

        if p_create_tables:
            persistence_base.Base.metadata.create_all(self._engine)

    def check_create_table_engine(self):

        if self._create_table_engine is None:
            msg = "Admin credentials for database not supplied -> skipping --create-databases!"
            self._logger.info(msg)
            return False

        return True

    def check_schema(self, p_create_tables=True):

        msg = "Checking whether to create database '{name}'..."
        self._logger.info(msg.format(name=self._config.database_name))

        if persistence_base.DATABASE_DRIVER_POSTGRESQL in self._config.database_driver:
            self.create_postgresql(p_create_tables=p_create_tables)

        elif persistence_base.DATABASE_DRIVER_MYSQL in self._config.database_driver:
            self.create_mysql(p_create_tables=p_create_tables)

        elif persistence_base.DATABASE_DRIVER_SQLITE in self._config.database_driver:
            self.create_sqlite(p_create_tables=p_create_tables)

        else:
            fmt = "Unknown database driver '{driver}'. Known drivers: {drivers}"
            raise configuration.ConfigurationException(
                fmt.format(driver=self._config.database_driver,
                           drivers="'" + "', '".join(persistence_base.DATABASE_DRIVERS) + "'"))

    def log_admin_event(self, p_admin_event):

        session = self.get_session()
        event = create_class_instance(persistent_admin_event.AdminEvent, p_initial_values=p_admin_event)
        session.add(event)
        session.commit()
        session.close()

    def write_process_info(self, p_process_info):

        session = self.get_session()
        exists = session.query(sqlalchemy.exists().where(
            persistent_process_info.ProcessInfo.key == p_process_info.get_key())).scalar()

        if not exists:
            pinfo = create_class_instance(persistent_process_info.ProcessInfo, p_initial_values=p_process_info)
            pinfo.key = p_process_info.get_key()
            session.add(pinfo)

        session.commit()
        session.close()

    def update_process_info(self, p_process_info):

        session = self.get_session()
        pinfo = session.query(persistent_process_info.ProcessInfo).filter(
            persistent_process_info.ProcessInfo.key == p_process_info.get_key()).one()
        pinfo.end_time = p_process_info.end_time
        pinfo.downtime = p_process_info.downtime
        session.commit()
        session.close()

    def update_rule_override(self, p_rule_override):

        session = self.get_session()
        query = session.query(persistent_rule_override.RuleOverride).filter(
            persistent_rule_override.RuleOverride.key == p_rule_override.get_key())

        if query.count() == 1:
            override = query.one()
            override.min_time_of_day = p_rule_override.min_time_of_day
            override.max_time_of_day = p_rule_override.max_time_of_day
            override.max_time_per_day = p_rule_override.max_time_per_day
            override.min_break = p_rule_override.min_break
            override.free_play = p_rule_override.free_play
            override.max_activity_duration = p_rule_override.max_activity_duration

        else:
            override = create_class_instance(persistent_rule_override.RuleOverride, p_initial_values=p_rule_override)
            override.key = p_rule_override.get_key()
            session.add(override)

        session.commit()
        session.close()

    def load_process_infos(self, p_lookback_in_days):

        with SessionContext(self) as session_context:
            #            session_context = SessionContext(self)
            session = session_context.get_session()
            reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)

            result = session.query(persistent_process_info.ProcessInfo).filter(
                persistent_process_info.ProcessInfo.start_time > reference_time).all()

            for pinfo in result:
                device = self.hostname_device_map(session_context).get(pinfo.hostname)

                if device is not None:
                    pinfo.hostlabel = device.device_name

                else:
                    pinfo.hostlabel = None

        return result

    def delete_historic_entries(self, p_history_length_in_days):

        msg = "Deleting historic entries older than {days} days..."
        self._logger.info(msg.format(days=p_history_length_in_days))

        with SessionContext(self) as session_context:
            session = session_context.get_session()
            reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_history_length_in_days)
            reference_date = reference_time.date()

            result = session.query(persistent_rule_override.RuleOverride).filter(
                persistent_rule_override.RuleOverride.reference_date < reference_date).all()

            msg = "Deleting {count} rule override entries..."
            self._logger.info(msg.format(count=len(result)))

            for override in result:
                session.delete(override)

            result = session.query(persistent_admin_event.AdminEvent).filter(
                persistent_admin_event.AdminEvent.event_time < reference_time).all()

            msg = "Deleting {count} admin events..."
            self._logger.info(msg.format(count=len(result)))

            for event in result:
                session.delete(event)

            result = session.query(persistent_process_info.ProcessInfo).filter(
                persistent_process_info.ProcessInfo.start_time < reference_time).all()

            msg = "Deleting {count} process infos..."
            self._logger.info(msg.format(count=len(result)))

            for pinfo in result:
                session.delete(pinfo)

            session.commit()

    def load_rule_overrides(self, p_lookback_in_days):

        session = self.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)
        result = session.query(persistent_rule_override.RuleOverride).filter(
            persistent_rule_override.RuleOverride.reference_date > reference_time).all()
        session.close()
        return result

    def truncate_table(self, p_entity):

        session = self.get_session()
        session.query(p_entity).delete()
        session.commit()
        session.close()

    def devices(self, p_session_context):

        current_devices = p_session_context.get_cache("devices")

        if current_devices is None:
            session = p_session_context.get_session()
            current_devices = session.query(persistent_device.Device).options().all()
            p_session_context.set_cache(p_name="devices", p_object=current_devices)

        return current_devices

    def device_map(self, p_session_context):

        return {device.device_name: device for device in self.devices(p_session_context=p_session_context)}

    def hostname_device_map(self, p_session_context):

        return {device.hostname: device for device in self.devices(p_session_context=p_session_context)}

    def clear_cache(self):
        SessionContext.clear_caches()

    def add_new_device(self, p_session_context, p_name_pattern):

        session = self.get_session()
        new_device = persistent_device.Device()
        new_device.device_name = tools.get_new_object_name(
            p_name_pattern=p_name_pattern,
            p_existing_names=[device.device_name for device in self.devices(p_session_context)])
        new_device.sample_size = constants.DEFAULT_DEVICE_SAMPLE_SIZE
        new_device.min_activity_duration = constants.DEFAULT_DEVICE_MIN_ACTIVITY_DURATION
        new_device.max_active_ping_delay = constants.DEFAULT_DEVICE_MAX_ACTIVE_PING_DELAY
        session.add(new_device)

        session.commit()
        session.close()
        self.clear_cache()


    def delete_user2device(self, p_user2device_id):

        session = self.get_session()
        user2device = persistent_user_2_device.User2Device.get_by_id(p_session=session, p_id=p_user2device_id)

        if user2device is None:
            msg = "Cannot delete user2device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_user2device_id))
            session.close()
            return

        session.delete(user2device)
        session.commit()
        session.close()
        self.clear_cache()

    def delete_device(self, p_id):

        session = self.get_session()
        device = persistent_device.Device.get_by_id(p_session=session, p_id=p_id)

        if device is None:
            msg = "Cannot delete device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_id))
            session.close()
            return

        for user2device in device.users:
            session.delete(user2device)

        session.delete(device)
        session.commit()
        session.close()
        self.clear_cache()

    def add_device(self, p_username, p_device_id):

        session = self.get_session()
        user = persistent_user.User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg = "Cannot add device to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            session.close()
            return

        device = persistent_device.Device.get_by_id(p_session=session, p_id=p_device_id)

        if device is None:
            msg = "Cannot add device id {id} to user {username}. Not in database!"
            self._logger.warning(msg.format(id=p_device_id, username=p_username))
            session.close()
            return

        user2device = persistent_user_2_device.User2Device()
        user2device.user = user
        user2device.device = device
        user2device.active = False
        user2device.percent = 100

        session.add(user2device)

        session.commit()
        session.close()
        self.clear_cache()
