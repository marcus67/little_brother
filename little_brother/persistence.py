# -*- coding: utf-8 -*-

# Copyright (C) 2019  Marcus Rickert
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
import re
import urllib.parse

import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Boolean, ForeignKey
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import relationship

from little_brother import constants
from little_brother import rule_handler
from little_brother import simple_context_rule_handlers
from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

_ = lambda x: x

Base = sqlalchemy.ext.declarative.declarative_base()

SECTION_NAME = "Persistence"

DATABASE_DRIVER_MYSQL = 'mysql'
DATABASE_DRIVER_POSTGRESQL = 'postgresql'
DATABASE_DRIVER_SQLITE = 'sqlite'

DATABASE_DRIVERS = [
    DATABASE_DRIVER_MYSQL,
    DATABASE_DRIVER_POSTGRESQL,
    DATABASE_DRIVER_SQLITE
]

#: Default value for option :class:`PersistenceConfigModel.pool_recycle`
DEFAULT_POOL_RECYCLE = 3600

class ProcessInfo(Base):
    __tablename__ = 'process_info'

    id = Column(Integer, primary_key=True)
    key = Column(String(256))
    hostname = Column(String(256))
    username = Column(String(256))
    pid = Column(Integer)
    processhandler = Column(String(1024))
    processname = Column(String(1024))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    downtime = Column(Integer, server_default="0")
    percent = Column(Integer, server_default="100")


class AdminEvent(Base):
    __tablename__ = 'admin_event'

    id = Column(Integer, primary_key=True)
    hostname = Column(String(256))
    username = Column(String(256))
    pid = Column(Integer)
    processhandler = Column(String(1024))
    processname = Column(String(1024))
    event_type = Column(String(256))
    event_time = Column(DateTime)
    process_start_time = Column(DateTime)
    downtime = Column(Integer, server_default="0")


class RuleOverride(Base):
    __tablename__ = 'rule_override'

    id = Column(Integer, primary_key=True)
    key = Column(String(256))
    username = Column(String(256))
    reference_date = Column(Date)
    max_time_per_day = Column(Integer)
    min_time_of_day = Column(Time)
    max_time_of_day = Column(Time)
    min_break = Column(Integer)
    free_play = Column(Boolean)
    max_activity_duration = Column(Integer)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    process_name_pattern = Column(String(256))
    username = Column(String(256))
    first_name = Column(String(256))
    last_name = Column(String(256))
    locale = Column(String(5))
    active = Column(Boolean)
    rulesets = relationship("RuleSet", back_populates="user", lazy="joined")
    devices = relationship("User2Device", back_populates="user", lazy="joined")

    def __init__(self):

        self.process_name_pattern = None
        self.username = None
        self.first_name = None
        self.last_name = None
        self.locale = None
        self.active = False

        self.init_on_load()

    @staticmethod
    def get_by_username(p_session, p_username):
        query = p_session.query(User).filter(User.username == p_username)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @property
    def notification_name(self):
        if self.first_name is not None and self.first_name != '':
            return self.first_name

        else:
            return self.username.capitalize()

    @property
    def full_name(self):
        if self.first_name is not None and self.first_name != '':
            if self.last_name is not None and self.last_name != '':
                return self.first_name + " " + self.last_name

            else:
                return self.first_name

        else:
            return self.username.capitalize()

    @property
    def device_list(self):
        if len(self.devices) == 0:
            return tools.value_or_not_set(None)

        else:
            return ", ".join([user2device.device.device_name for user2device in self.devices])

    @property
    def html_key(self):
        return "user_{id}".format(id=self.id)

    @property
    def rulesets_html_key(self):
        return "rulesets_user_{id}".format(id=self.id)

    @property
    def devices_html_key(self):
        return "devices_user_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_user_{id}".format(id=self.id)

    @property
    def new_ruleset_html_key(self):
        return "new_ruleset_user_{id}".format(id=self.id)

    @property
    def new_device_html_key(self):
        return "new_device_user_{id}".format(id=self.id)

    @sqlalchemy.orm.reconstructor
    def init_on_load(self):
        self._regex_process_name_pattern = None

    @property
    def regex_process_name_pattern(self):

        if self._regex_process_name_pattern is None:
            self._regex_process_name_pattern = re.compile(self.process_name_pattern)

        return self._regex_process_name_pattern

    @property
    def sorted_rulesets(self):
        return sorted(self.rulesets, key=lambda ruleset:-ruleset.priority)

    @property
    def sorted_user2devices(self):
        return sorted(self.devices, key=lambda user2device:(-user2device.percent, user2device.device.device_name))

    @property
    def summary(self):

        texts = []

        if self.username.upper() != self.full_name.upper():
            texts.extend([_("Username"), ":", self.username])

        texts.extend([constants.TEXT_SEPERATOR, _("Monitored"), ": ", tools.format_boolean(p_value=self.active)])

        if self.locale is not None:
            lang = constants.LANGUAGES.get(self.locale)

            if lang is None:
                lang = _("Unknown")

            texts.extend([constants.TEXT_SEPERATOR, _("Locale"), ": ", lang])

        return texts

    def __str__(self):
        fmt = "User (username='{username}, active={active}, process_name_pattern='{process_name_pattern}')"
        return fmt.format(username=self.username, active=self.active, process_name_pattern=self.process_name_pattern)


class Device(Base):
    __tablename__ = 'device'

    id = Column(Integer, primary_key=True)
    device_name = Column(String(256), nullable=False)
    hostname = Column(String(256))
    min_activity_duration = Column(Integer)
    max_active_ping_delay = Column(Integer)
    sample_size = Column(Integer)
    users = relationship("User2Device", back_populates="device", lazy="joined")

    def __init__(self):

        self.device_name = None
        self.hostname = None
        self.min_activity_duration = None
        self.max_active_ping_delay = None
        self.sample_size = None

    @staticmethod
    def get_by_device_name(p_session, p_device_name):
        query = p_session.query(Device).filter(Device.device_name == p_device_name)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @staticmethod
    def get_by_id(p_session, p_id):
        query = p_session.query(Device).filter(Device.id == p_id)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @property
    def html_key(self):
        return "device_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_device_{id}".format(id=self.id)

    def list_of_users(self, p_exclude=None):

        return ", ".join(["{name} ({percent}%)".format(name=user2device.user.full_name, percent=user2device.percent)
                          for user2device in self.users
                          if p_exclude is None or not user2device.user is p_exclude])

    @property
    def summary(self):
        texts = []

        if len(self.users) > 0:
            texts.extend([_("Assigned users"), ": ", self.list_of_users()])

        texts.extend([constants.TEXT_SEPERATOR, _("Host Name"), ": ", tools.value_or_not_set(self.hostname)])

        return texts


class User2Device(Base):
    __tablename__ = 'user2device'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    percent = Column(Integer)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="devices", lazy="joined")

    device_id = Column(Integer, ForeignKey("device.id"), nullable=False)
    device = relationship("Device", back_populates="users", lazy="joined")

    @property
    def summary(self):

        texts = [constants.TEXT_SEPERATOR, _("Monitored"), ": ", tools.format_boolean(p_value=self.active),
                 constants.TEXT_SEPERATOR, "{percent}%".format(percent=self.percent)]

        if len(self.device.users) > 1:
            texts.extend([constants.TEXT_SEPERATOR, _("Shared with"), ": ",
                          self.device.list_of_users(p_exclude=self.user)])

        return texts

    @staticmethod
    def get_by_id(p_session, p_id):
        query = p_session.query(User2Device).filter(User2Device.id == p_id)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @property
    def html_key(self):
        return "user2device_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_user2device_{id}".format(id=self.id)


class RuleSet(Base):
    __tablename__ = 'ruleset'

    id = Column(Integer, primary_key=True)

    context_label = Column(String(256))
    context = Column(String(256))
    context_details = Column(String(256))
    priority = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="rulesets", lazy="joined")
    min_time_of_day = Column(Time)
    max_time_of_day = Column(Time)
    max_time_per_day = Column(Integer)
    max_activity_duration = Column(Integer)
    min_break = Column(Integer)
    free_play = Column(Boolean)

    def __init__(self):

        self.context = None
        self.context_details = None
        self.context_label = None
        self.min_time_of_day = None
        self.max_time_of_day = None
        self.max_time_per_day = None
        self.max_activity_duration = None
        self.min_break = None
        self.free_play = False
        self.priority = None
        self.get_context_rule_handler = None

    @property
    def label(self):
        if self.context_label:
            return self.context_label

        else:
            return self.context

    @property
    def summary(self):
        context_handler = self.get_context_rule_handler(p_context_name=self.context)

        texts = []

        if context_handler is not None:
            texts.extend(context_handler.summary(p_context_detail=self.context_details))

        if self.max_time_per_day is not None:
            texts.append(constants.TEXT_SEPERATOR)
            texts.append("Time per Day")
            texts.append(": " + tools.get_duration_as_string(p_seconds=self.max_time_per_day, p_include_seconds=False))

        return texts


    @property
    def html_key(self):
        return "ruleset_{id}".format(id=self.id)

    @property
    def delete_html_key(self):
        return "delete_ruleset_{id}".format(id=self.id)

    @property
    def move_up_html_key(self):
        return "move_up_ruleset_{id}".format(id=self.id)

    @property
    def move_down_html_key(self):
        return "move_down_ruleset_{id}".format(id=self.id)

    @staticmethod
    def get_by_id(p_session, p_id):
        query = p_session.query(RuleSet).filter(RuleSet.id == p_id)

        if query.count() == 1:
            return query.one()

        else:
            return None

    @property
    def can_move_up(self):

        return 1 < self.priority < len(self.user.rulesets)

    @property
    def can_move_down(self):

        return self.priority > 2

    @property
    def fixed_context(self):

        return self.priority == 1


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
        self._users = None
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

            if DATABASE_DRIVER_POSTGRESQL in self._config.database_driver:
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

        if (DATABASE_DRIVER_POSTGRESQL in self._config.database_driver or
                DATABASE_DRIVER_MYSQL in self._config.database_driver):
            options['pool_size'] = self._config.pool_size
            options['max_overflow'] = self._config.max_overflow

        # if DATABASE_DRIVER_SQLITE in self._config.database_driver:
        #     options['check_same_thread'] = False

        self._engine = sqlalchemy.create_engine(url, **options)

    def build_url(self):

        if self._config.database_driver != DATABASE_DRIVER_SQLITE:
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
        return DATABASE_DRIVER_SQLITE not in self._config.database_driver

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
            Base.metadata.create_all(self._engine)

    def init_mysql(self):
        pass

    def create_postgresql(self, p_create_tables):

        if not self.check_create_table_engine():
            return

        fmt = "Creating user %s" % self._config.database_user
        self._logger.info(fmt)

        try:
            self._admin_engine.execute(
                "CREATE USER %s WITH PASSWORD '%s';" % (self._config.database_user, self._config.database_password))

        except ProgrammingError:
            fmt = "User %s already exists" % self._config.database_user
            self._logger.info(fmt)

        fmt = "Creating database %s" % self._config.database_name
        self._logger.info(fmt)

        try:
            self._create_table_engine.execute("CREATE DATABASE %s WITH OWNER = %s ENCODING = 'UTF8';" % (
                self._config.database_name, self._config.database_user))

        except ProgrammingError:
            fmt = "Database %s already exists" % self._config.database_name
            self._logger.info(fmt)
            return

        if p_create_tables:
            Base.metadata.create_all(self._engine)

    def create_sqlite(self, p_create_tables):

        if p_create_tables:
            Base.metadata.create_all(self._engine)

    def check_create_table_engine(self):

        if self._create_table_engine is None:
            msg = "Admin credentials for database not supplied -> skipping --create-databases!"
            self._logger.info(msg)
            return False

        return True

    def check_schema(self, p_create_tables=True):

        msg = "Checking whether to create database {name}..."
        self._logger.info(msg.format(name=self._config.database_name))

        if DATABASE_DRIVER_POSTGRESQL in self._config.database_driver:
            self.create_postgresql(p_create_tables=p_create_tables)

        elif DATABASE_DRIVER_MYSQL in self._config.database_driver:
            self.create_mysql(p_create_tables=p_create_tables)

        elif DATABASE_DRIVER_SQLITE in self._config.database_driver:
            self.create_sqlite(p_create_tables=p_create_tables)

        else:
            fmt = "Unknown database driver '{driver}'. Known drivers: {drivers}"
            raise configuration.ConfigurationException(
                fmt.format(driver=self._config.database_driver,
                           drivers="'" + "', '".join(DATABASE_DRIVERS) + "'"))

    def log_admin_event(self, p_admin_event):

        session = self.get_session()
        event = create_class_instance(AdminEvent, p_initial_values=p_admin_event)
        session.add(event)
        session.commit()
        session.close()

    def write_process_info(self, p_process_info):

        session = self.get_session()
        exists = session.query(sqlalchemy.exists().where(ProcessInfo.key == p_process_info.get_key())).scalar()

        if not exists:
            pinfo = create_class_instance(ProcessInfo, p_initial_values=p_process_info)
            pinfo.key = p_process_info.get_key()
            session.add(pinfo)

        session.commit()
        session.close()

    def update_process_info(self, p_process_info):

        session = self.get_session()
        pinfo = session.query(ProcessInfo).filter(ProcessInfo.key == p_process_info.get_key()).one()
        pinfo.end_time = p_process_info.end_time
        pinfo.downtime = p_process_info.downtime
        session.commit()
        session.close()

    def update_rule_override(self, p_rule_override):

        session = self.get_session()
        query = session.query(RuleOverride).filter(RuleOverride.key == p_rule_override.get_key())

        if query.count() == 1:
            override = query.one()
            override.min_time_of_day = p_rule_override.min_time_of_day
            override.max_time_of_day = p_rule_override.max_time_of_day
            override.max_time_per_day = p_rule_override.max_time_per_day
            override.min_break = p_rule_override.min_break
            override.free_play = p_rule_override.free_play
            override.max_activity_duration = p_rule_override.max_activity_duration

        else:
            override = create_class_instance(RuleOverride, p_initial_values=p_rule_override)
            override.key = p_rule_override.get_key()
            session.add(override)

        session.commit()
        session.close()

    def load_process_infos(self, p_lookback_in_days):

        with SessionContext(self) as session_context:
            session_context = SessionContext(self)
            session = session_context.get_session()
            reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)

            result = session.query(ProcessInfo).filter(ProcessInfo.start_time > reference_time).all()

            for pinfo in result:
                device = self.hostname_device_map(session_context).get(pinfo.hostname)

                if device is not None:
                    pinfo.hostlabel = device.device_name

                else:
                    pinfo.hostlabel = None

        return result

    def load_rule_overrides(self, p_lookback_in_days):

        session = self.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)
        result = session.query(RuleOverride).filter(RuleOverride.reference_date > reference_time).all()
        session.close()
        return result

    def truncate_table(self, p_entity):

        session = self.get_session()
        session.query(p_entity).delete()
        session.commit()
        session.close()

    def users(self, p_session_context):

        current_users = p_session_context.get_cache("users")

        if current_users is None:
            session = p_session_context.get_session()
            current_users = session.query(User).all()
            p_session_context.set_cache(p_name="users", p_object=current_users)

        return current_users

    def user_map(self, p_session_context):

        return {user.username: user for user in self.users(p_session_context=p_session_context)}

    def devices(self, p_session_context):

        current_devices = p_session_context.get_cache("devices")

        if current_devices is None:
            session = p_session_context.get_session()
            current_devices = session.query(Device).options().all()
            p_session_context.set_cache(p_name="devices", p_object=current_devices)

        return current_devices

    def device_map(self, p_session_context):

        return {device.device_name: device for device in self.devices(p_session_context=p_session_context)}

    def hostname_device_map(self, p_session_context):

        return {device.hostname: device for device in self.devices(p_session_context=p_session_context)}


    def clear_cache(self):
        SessionContext.clear_caches()

    def get_default_ruleset(self, p_priority=rule_handler.DEFAULT_PRIORITY):

        default_ruleset = RuleSet()
        default_ruleset.priority = p_priority
        default_ruleset.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME
        return default_ruleset

    def add_new_user(self, p_session_context, p_username, p_locale=None):

        if p_username in self.user_map(p_session_context):
            msg = "Cannot create new user {username}. Already in database!"
            self._logger.warning(msg.format(username=p_username))
            return

        session = self.get_session()
        new_user = User()
        new_user.username = p_username
        new_user.locale = p_locale
        new_user.process_name_pattern = constants.DEFAULT_PROCESS_NAME_PATTERN
        session.add(new_user)

        default_ruleset = self.get_default_ruleset()
        default_ruleset.user = new_user
        session.add(default_ruleset)

        session.commit()
        session.close()
        self.clear_cache()

    def add_new_device(self, p_session_context, p_name_pattern):

        session = self.get_session()
        new_device = Device()
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


    def delete_user(self, p_username):

        session = self.get_session()
        user = User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg =  "Cannot delete user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            return

        for ruleset in user.rulesets:
            session.delete(ruleset)

        for user2device in user.devices:
            session.delete(user2device)

        session.delete(user)
        session.commit()
        session.close()
        self.clear_cache()

    def delete_ruleset(self, p_ruleset_id):

        session = self.get_session()
        ruleset = RuleSet.get_by_id(p_session=session, p_id=p_ruleset_id)

        if ruleset is None:
            msg =  "Cannot delete ruleset {id}. Not in database!"
            self._logger.warning(msg.format(id=p_ruleset_id))
            session.close()
            return

        session.delete(ruleset)
        session.commit()
        session.close()
        self.clear_cache()

    def delete_user2device(self, p_user2device_id):

        session = self.get_session()
        user2device = User2Device.get_by_id(p_session=session, p_id=p_user2device_id)

        if user2device is None:
            msg =  "Cannot delete user2device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_user2device_id))
            session.close()
            return

        session.delete(user2device)
        session.commit()
        session.close()
        self.clear_cache()

    def delete_device(self, p_id):

        session = self.get_session()
        device = Device.get_by_id(p_session=session, p_id=p_id)

        if device is None:
            msg =  "Cannot delete device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_id))
            session.close()
            return

        for user2device in device.users:
            session.delete(user2device)

        session.delete(device)
        session.commit()
        session.close()
        self.clear_cache()

    def add_ruleset(self, p_username):

        session = self.get_session()
        user = User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg =  "Cannot add ruleset to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            session.close()
            return

        new_priority = max([ruleset.priority for ruleset in user.rulesets]) + 1

        default_ruleset = self.get_default_ruleset(p_priority=new_priority)
        default_ruleset.user = user
        session.add(default_ruleset)

        session.commit()
        session.close()
        self.clear_cache()

    def add_device(self, p_username, p_device_id):

        session = self.get_session()
        user = User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg =  "Cannot add device to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            session.close()
            return

        device = Device.get_by_id(p_session=session,    p_id=p_device_id)

        if device is None:
            msg =  "Cannot add device id {id} to user {username}. Not in database!"
            self._logger.warning(msg.format(id=p_device_id, username=p_username))
            session.close()
            return

        user2device = User2Device()
        user2device.user = user
        user2device.device = device
        user2device.active = False
        user2device.percent = 100

        session.add(user2device)

        session.commit()
        session.close()
        self.clear_cache()

    def move_ruleset(self, p_ruleset, p_sorted_rulesets):

        found = False
        index = 0

        while not found:
            if p_sorted_rulesets[index].priority == p_ruleset.priority:
                found = True

            else:
                index += 1

        other_ruleset = p_sorted_rulesets[index + 1]

        tmp = p_ruleset.priority
        p_ruleset.priority = other_ruleset.priority
        other_ruleset.priority = tmp

    def move_up_ruleset(self, p_ruleset_id):

        session = self.get_session()

        ruleset = RuleSet.get_by_id(p_session=session, p_id=p_ruleset_id)
        sorted_rulesets = sorted(ruleset.user.rulesets, key=lambda ruleset:ruleset.priority)
        self.move_ruleset(p_ruleset=ruleset, p_sorted_rulesets=sorted_rulesets)

        session.commit()
        session.close()
        self.clear_cache()

    def move_down_ruleset(self, p_ruleset_id):

        session = self.get_session()

        ruleset = RuleSet.get_by_id(p_session=session, p_id=p_ruleset_id)
        sorted_rulesets = sorted(ruleset.user.rulesets, key=lambda ruleset: -ruleset.priority)
        self.move_ruleset(p_ruleset=ruleset, p_sorted_rulesets=sorted_rulesets)

        session.commit()
        session.close()
        self.clear_cache()
