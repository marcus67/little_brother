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
import urllib.parse
import re

import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Boolean, ForeignKey, Table
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import relationship, contains_eager, joinedload

from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

from little_brother import constants
from little_brother import rule_handler
from little_brother import simple_context_rule_handlers

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
    def html_key(self):
        return "user_{id}".format(id=self.id)

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


class User2Device(Base):
    __tablename__ = 'user2device'

    id = Column(Integer, primary_key=True)
    active = Column(Boolean)
    percent = Column(Integer)

    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    user = relationship("User", back_populates="devices", lazy="joined")

    device_id = Column(Integer, ForeignKey("device.id"), nullable=False)
    device = relationship("Device", back_populates="users", lazy="joined")

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

    @property
    def details(self):
        return "TODO"

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

    @property
    def label(self):
        if self.context_label:
            return self.context_label

        else:
            return self.context


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
        self.database_user = 'little_brother'
        self.database_password = None
        self.database_admin = 'postgres'
        self.database_admin_password = None

        #: Number of seconds that a database connection will be kept in the pool before it is discarded.
        #: It has to be shorter than the maximum time that a database server will keep a connection alive.
        #: In case of MySql this will be eight hours.
        #: See https://stackoverflow.com/questions/6471549/avoiding-mysql-server-has-gone-away-on-infrequently-used-python-flask-server
        #: Default value: :data:``
        self.pool_recycle = 3600


class Persistence(object):

    def __init__(self, p_config, p_reuse_session=True):

        self._logger = log_handling.get_logger(self.__class__.__name__)
        self._config = p_config
        self._session_used = False
        self._admin_session = None
        self._create_table_session = None
        self._admin_engine = None
        self._reuse_session = p_reuse_session
        self._users = None
        self._devices = None

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

        self._engine = sqlalchemy.create_engine(url, pool_recycle=self._config.pool_recycle)

    def build_url(self):

        if self._config.database_user is not None:
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
            url = "{driver}://".format(driver=self._config.database_driver)

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

    def get_session(self):
        if not self._session_used:
            fmt = "Open database for normal access"
            self._logger.info(fmt)
            self._session_used = True

        return sqlalchemy.orm.sessionmaker(bind=self._engine)()

    def create_mysql(self, p_create_tables):
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

    def check_schema(self, p_create_tables=True):
        if self._admin_engine is None and self._config.database_admin is not None:
            raise configuration.ConfigurationException(
                "check_schema () called without [Persistence].database_admin "
                "and [Persistence].database_admin_password set")

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

        if not self._reuse_session:
            session.close()

    def write_process_info(self, p_process_info):

        session = self.get_session()
        exists = session.query(sqlalchemy.exists().where(ProcessInfo.key == p_process_info.get_key())).scalar()

        if not exists:
            pinfo = create_class_instance(ProcessInfo, p_initial_values=p_process_info)
            pinfo.key = p_process_info.get_key()
            session.add(pinfo)

        session.commit()

        if not self._reuse_session:
            session.close()

    def update_process_info(self, p_process_info):

        session = self.get_session()
        pinfo = session.query(ProcessInfo).filter(ProcessInfo.key == p_process_info.get_key()).one()
        pinfo.end_time = p_process_info.end_time
        pinfo.downtime = p_process_info.downtime
        session.commit()

        if not self._reuse_session:
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

        if not self._reuse_session:
            session.close()

    def load_process_infos(self, p_lookback_in_days):

        session = self.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)

        result = session.query(ProcessInfo).filter(ProcessInfo.start_time > reference_time).all()

        if not self._reuse_session:
            session.close()

        return result

    def load_rule_overrides(self, p_lookback_in_days):

        session = self.get_session()
        reference_time = datetime.datetime.now() + datetime.timedelta(days=-p_lookback_in_days)

        result = session.query(RuleOverride).filter(RuleOverride.reference_date > reference_time).all()

        if not self._reuse_session:
            session.close()

        return result

    def truncate_table(self, p_entity):

        session = self.get_session()
        session.query(p_entity).delete()
        session.commit()

        if not self._reuse_session:
            session.close()

    @property
    def users(self):

        if self._users is None:
            session = self.get_session()
            self._users = session.query(User).options(joinedload(User.rulesets), contains_eager('rulesets.user')).all()

        return self._users


    @property
    def user_map(self):

        return { user.username:user for user in self.users }

    @property
    def devices(self):

        if self._devices is None:
            session = self.get_session()
            self._devices = session.query(Device).all()

        return self._devices


    def clear_cache(self):
        self._users = None
        self._devices = None

    def get_default_ruleset(self, p_priority=rule_handler.DEFAULT_PRIORITY):

        default_ruleset = RuleSet()
        default_ruleset.priority = p_priority
        default_ruleset.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME
        return default_ruleset

    def add_new_user(self, p_username, p_locale=None):

        if p_username in self.user_map:
            msg =  "Cannot create new user {username}. Already in database!"
            self._logger.warning(msg.format(username=p_username))
            return

        session = self.get_session()
        new_user = User()
        new_user.username = p_username
        new_user.locale = p_locale
        new_user.process_name_pattern = rule_handler.DEFAULT_PROCESS_PATTERN
        session.add(new_user)

        default_ruleset = self.get_default_ruleset()
        default_ruleset.user = new_user
        session.add(default_ruleset)

        session.commit()
        self.clear_cache()

    def add_new_device(self, p_name_pattern):

        session = self.get_session()
        new_device = Device()
        new_device.device_name = tools.get_new_object_name(
            p_name_pattern=p_name_pattern,
            p_existing_names=[device.device_name for device in self.devices])
        new_device.sample_size = constants.DEFAULT_DEVICE_SAMPLE_SIZE
        new_device.min_activity_duration = constants.DEFAULT_DEVICE_MIN_ACTIVITY_DURATION
        new_device.max_active_ping_delay = constants.DEFAULT_DEVICE_MAX_ACTIVE_PING_DELAY
        session.add(new_device)

        session.commit()
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
        self.clear_cache()

    def delete_ruleset(self, p_ruleset_id):

        session = self.get_session()
        ruleset = RuleSet.get_by_id(p_session=session, p_id=p_ruleset_id)

        if ruleset is None:
            msg =  "Cannot delete ruleset {id}. Not in database!"
            self._logger.warning(msg.format(id=p_ruleset_id))
            return

        session.delete(ruleset)
        session.commit()
        self.clear_cache()

    def delete_user2device(self, p_user2device_id):

        session = self.get_session()
        user2device = User2Device.get_by_id(p_session=session, p_id=p_user2device_id)

        if user2device is None:
            msg =  "Cannot delete user2device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_user2device_id))
            return

        session.delete(user2device)
        session.commit()
        self.clear_cache()

    def delete_device(self, p_id):

        session = self.get_session()
        device = Device.get_by_id(p_session=session, p_id=p_id)

        if device is None:
            msg =  "Cannot delete device {id}. Not in database!"
            self._logger.warning(msg.format(id=p_id))
            return

        for user2device in device.users:
            session.delete(user2device)

        session.delete(device)
        session.commit()
        self.clear_cache()

    def add_ruleset(self, p_username):

        session = self.get_session()
        user = User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg =  "Cannot add ruleset to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            return

        new_priority = max([ruleset.priority for ruleset in user.rulesets]) + 1

        default_ruleset = self.get_default_ruleset(p_priority=new_priority)
        default_ruleset.user     = user
        session.add(default_ruleset)

        session.commit()
        self.clear_cache()

    def add_device(self, p_username, p_device_id):

        session = self.get_session()
        user = User.get_by_username(p_session=session, p_username=p_username)

        if user is None:
            msg =  "Cannot add device to user {username}. Not in database!"
            self._logger.warning(msg.format(username=p_username))
            return

        device = Device.get_by_id(p_session=session,    p_id=p_device_id)

        if device is None:
            msg =  "Cannot add device id {id} to user {username}. Not in database!"
            self._logger.warning(msg.format(id=p_device_id, username=p_username))
            return

        user2device = User2Device()
        user2device.user = user
        user2device.device = device
        user2device.active = False
        user2device.percent = 100

        session.add(user2device)

        session.commit()
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
        self.clear_cache()

    def move_down_ruleset(self, p_ruleset_id):

        session = self.get_session()

        ruleset = RuleSet.get_by_id(p_session=session, p_id=p_ruleset_id)
        sorted_rulesets = sorted(ruleset.user.rulesets, key=lambda ruleset: -ruleset.priority)
        self.move_ruleset(p_ruleset=ruleset, p_sorted_rulesets=sorted_rulesets)

        session.commit()
        self.clear_cache()

