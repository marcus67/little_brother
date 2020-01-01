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

import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy import Column, Integer, String, DateTime, Date, Time, Boolean
from sqlalchemy.exc import ProgrammingError

from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

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


def copy_attributes(p_from, p_to):
    for (key, value) in p_from.__dict__.items():
        if not key.startswith('_'):
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
