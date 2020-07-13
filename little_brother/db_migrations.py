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

import os.path

import alembic
import alembic.config

from little_brother import constants
from little_brother import persistence
from little_brother import rule_handler
from little_brother import simple_context_rule_handlers


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
        os.chdir(alembic_working_dir)
        alembic.config.main(alembic_argv, prog="alembic.config.main")

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

            user = persistence.User()
            session.add(user)

            user.username = username

            process_name_pattern = None
            locale = None

            for old_ruleset in configs:
                ruleset = persistence.RuleSet()
                session.add(ruleset)
                ruleset.user = user
                persistence.copy_attributes(p_from=old_ruleset, p_to=ruleset, p_only_existing=True)

                if ruleset.priority is None:
                    ruleset.priority = rule_handler.DEFAULT_PRIORITY

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

    def migrate_client_device_configs(self, p_client_device_configs):

        session = self._persistence.get_session()

        for device_name, old_device in p_client_device_configs.items():
            msg = "Migrating device '{device_name}..."
            self._logger.info(msg.format(device_name=device_name))

            device = persistence.Device()
            session.add(device)
            device.device_name = device_name
            persistence.copy_attributes(p_from=old_device, p_to=device, p_only_existing=True)

            if old_device.username is not None:
                query = session.query(persistence.User).filter(persistence.User.username == old_device.username)

                if query.count() == 1:
                    user = query.one()
                    user2device = persistence.User2Device()
                    user2device.device = device
                    user2device.percent = constants.DEFAULT_USER2DEVICE_PERCENT
                    user2device.active = True
                    user2device.user = user

                else:
                    msg = "Username '{username}' for found for device '{device_name}' -> not linking to user!"
                    self._logger.warning(msg.format(username=old_device.username, device_name=device_name))

        session.commit()
        session.close()
