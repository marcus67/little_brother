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

import alembic
import alembic.config

from little_brother import constants
from little_brother import simple_context_rule_handlers
# The following import is required by alembic migrations triggered by the test cases. Otherwise the entity "UserStatus"
# will not be found.
# noinspection PyUnresolvedReferences
from little_brother.persistence.persistent_daily_user_status import DailyUserStatus
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.persistent_rule_set import RuleSet
from little_brother.persistence.persistent_user import User
from little_brother.persistence.persistent_user_2_device import User2Device
from python_base_app import tools


class DatabaseMigrations(object):

    def __init__(self, p_logger, p_persistence):

        self._logger = p_logger
        self._persistence = p_persistence

    def upgrade_databases(self, p_alembic_version="head"):

        url = self._persistence.build_url()
        alembic_working_dir = os.path.dirname(__file__)

        fmt = "Upgrading database to revision '{revision}' using alembic with working directory {working_dir}..."
        self._logger.info(fmt.format(revision=p_alembic_version,
                                     working_dir=alembic_working_dir))

        alembic_argv = ["-x", url,
                        "upgrade", p_alembic_version]
        cwd = os.getcwd()
        os.chdir(alembic_working_dir)
        alembic.config.main(alembic_argv, prog="alembic.config.main")
        os.chdir(cwd)

    def get_current_version(self):

        context = alembic.migration.MigrationContext.configure(self._persistence.get_connection())
        return context.get_current_revision()

    def check_if_version_is_active(self, p_version):

        from alembic.script import ScriptDirectory
        from alembic.config import Config
        config = Config()
        config.set_main_option("script_location", "little_brother:alembic")
        script = ScriptDirectory.from_config(config)

        revision = script.get_revision(p_version)
        return revision is not None

    def migrate_ruleset_configs(self, p_ruleset_configs):

        session = self._persistence.get_session()

        for username, configs in p_ruleset_configs.items():
            msg = "Migrating username '{username}..."
            self._logger.info(msg.format(username=username))

            user = User()
            session.add(user)

            user.username = username

            process_name_pattern = None
            locale = None

            for old_ruleset in configs:
                ruleset = RuleSet()
                session.add(ruleset)
                ruleset.user = user
                tools.copy_attributes(p_from=old_ruleset, p_to=ruleset, p_only_existing=True)

                if ruleset.priority is None:
                    ruleset.priority = constants.DEFAULT_RULE_SET_PRIORITY

                if process_name_pattern is None and old_ruleset.process_name_pattern is not None:
                    process_name_pattern = old_ruleset.process_name_pattern

                if locale is None and old_ruleset.locale is not None:
                    locale = old_ruleset.locale

                if ruleset.context is None:
                    ruleset.context = simple_context_rule_handlers.DEFAULT_CONTEXT_RULE_HANDLER_NAME

                elif ruleset.context == 'weekday':
                    ruleset.context = simple_context_rule_handlers.WEEKPLAN_CONTEXT_RULE_HANDLER_NAME

            if process_name_pattern is None:
                process_name_pattern = constants.DEFAULT_PROCESS_NAME_PATTERN

            user.process_name_pattern = process_name_pattern
            user.locale = locale

        session.commit()
        session.close()

    def migrate_client_device_configs(self, p_client_device_configs, persistent_user2device=None):

        session = self._persistence.get_session()

        for device_name, old_device in p_client_device_configs.items():
            msg = "Migrating device '{device_name}..."
            self._logger.info(msg.format(device_name=device_name))

            device = Device()
            session.add(device)
            device.device_name = device_name
            tools.copy_attributes(p_from=old_device, p_to=device, p_only_existing=True)

            if old_device.username is not None:
                query = session.query(User).filter(User.username == old_device.username)

                if query.count() == 1:
                    user = query.one()
                    user2device = User2Device()
                    user2device.device = device
                    user2device.percent = constants.DEFAULT_USER2DEVICE_PERCENT
                    user2device.active = True
                    user2device.user = user

                else:
                    msg = "Username '{username}' for found for device '{device_name}' -> not linking to user!"
                    self._logger.warning(msg.format(username=old_device.username, device_name=device_name))

        session.commit()
        session.close()
