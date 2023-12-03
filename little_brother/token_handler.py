# -*- coding: utf-8 -*-
#    Copyright (C) 2019-2023  Marcus Rickert
#
#    See https://github.com/marcus67/python_base_app
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License along
#    with this program; if not, write to the Free Software Foundation, Inc.,
#    51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import datetime
from secrets import compare_digest
from typing import Optional

from little_brother.persistence.persistence import Persistence
from little_brother.persistence.persistent_blacklisted_token import BlacklistedToken
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from python_base_app.base_app import RecurringTask
from python_base_app.base_token_handler import BaseTokenHandler, BaseTokenHandlerConfigModel, SECTION_NAME as BASE_SECTION_NAME

SECTION_NAME = BASE_SECTION_NAME

class TokenHandler(PersistenceDependencyInjectionMixIn, BaseTokenHandler):

    def __init__(self, p_config: BaseTokenHandlerConfigModel, p_secret_key: str):
        super().__init__(p_config=p_config, p_secret_key=p_secret_key)

    def _store_blacklisted_token(self, p_token: str, p_deletion_time: datetime.datetime = None):

        if p_deletion_time is None:
            p_deletion_time = datetime.datetime.utcnow()

        session = self.persistence.get_session()

        blacklisted_token = BlacklistedToken()
        blacklisted_token.token = p_token
        blacklisted_token.deletion_time = p_deletion_time
        session.add(blacklisted_token)

        try:
            session.commit()

        except Exception as e:
            self._logger.error(f"Cannot store blacklisted token {p_token}!")
            raise e

        finally:
            session.close()

    def _is_token_blacklisted(self, p_token: str) -> bool:

        session = self.persistence.get_session()

        try:
            query = session.query(BlacklistedToken).filter(BlacklistedToken.token == p_token)
            return query.count() >= 1

        except Exception as e:
            self._logger.error(
                f"Cannot check if token {p_token} is blacklisted! Assuming that it is to be on the safe side. "
                f"Exception: {str(e)}")
            return True

        finally:
            session.close()

    def _clean_out_tokens(self, p_reference_time: datetime.datetime = None):

        if p_reference_time is None:
            p_reference_time = datetime.datetime.utcnow()

        cut_off_time = p_reference_time + datetime.timedelta(days=-self._config.max_token_age_in_days)

        session = self.persistence.get_session()

        try:
            tokens_to_be_deleted = \
                self.blacklisted_token_entity_manager.get_old_tokens(p_session=session, p_cut_off_time=cut_off_time)
            count = len(tokens_to_be_deleted)

            for token in tokens_to_be_deleted:
                session.delete(token)

            session.commit()

        except Exception as e:
            self._logger.error(f"Exception '{str(e)}' while cleaning out old auth tokens.")
            return 0

        finally:
            session.close()

        return count

    def get_recurring_task(self) -> Optional[RecurringTask]:
        return RecurringTask(
            p_name="TokenHandler.cleanup",
            p_handler_method=lambda: self.cleanup(),
            p_interval=self._config.token_cleanup_interval_in_hours * 3600,
            p_ignore_exceptions=True)
