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

import os.path
import urllib.parse

import sqlalchemy.ext.declarative
import sqlalchemy.orm
from sqlalchemy.exc import ProgrammingError

from little_brother.persistence import persistence_base
from little_brother.persistence.session_context import SessionContext
from python_base_app import configuration
from python_base_app import log_handling
from python_base_app import tools

SECTION_NAME = "Persistence"


def _(x):
    return x


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
                sqlite_filename = self.get_database_filename(p_config=self._config)
                url = "{driver}:///{filename}".format(driver=self._config.database_driver, filename=sqlite_filename)

        return url

    @classmethod
    def get_database_filename(cls, p_config):
        return os.path.join(p_config.sqlite_dir, p_config.sqlite_filename)

    @classmethod
    def delete_database(cls, p_logger, p_config):
        filename = cls.get_database_filename(p_config=p_config)

        if os.path.exists(filename):
            msg = "Deleting database file '{filename}'"
            p_logger.info(msg.format(filename=filename))
            os.unlink(filename)

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

    def truncate_table(self, p_entity):

        session = self.get_session()
        session.query(p_entity).delete()
        session.commit()
        session.close()

    def count_rows(self, p_entity):

        with SessionContext(self) as session_context:
            return session_context.get_session().query(p_entity).count()

    def clear_cache(self):
        SessionContext.clear_caches()
