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

import collections
import datetime
import json

import requests

from little_brother import context_rule_handler
from python_base_app import configuration
from python_base_app import log_handling

# Dummy function to trigger extraction by pybabel...
_ = lambda x: x

_("vacation")

CALENDAR_CONTEXT_RULE_HANDLER_NAME = "german-vacation-calendar"

SECTION_NAME = "GermanVacationCalendar"

ENTRY_FILTER = [
    'Herbst',
    'Weihnachten',
    'Sommer',
    'Himmelfahrt',
    'Ostern',
    'Allerheiligen',
    'Christi Himmelfahrt',
    'Pfingstmontag',
    'Reformationstag',
    'Buß- und Bettag',
    'Heilige Drei Könige',
    'Mariä Himmelfahrt',
    'Pfingsten',
    'Schulschließung wegen der COVID-19-Pandemie (Corona)'
]

VacationEntry = collections.namedtuple("VacationEntry", ["name", "start_date", "end_date"])


class GermanVacationContextRuleHandlerConfig(configuration.ConfigModel):

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        # See https://www.mehr-schulferien.de
        self.locations_url = "https://www.mehr-schulferien.de/api/v2.0/locations"
        self.vacation_data_url = "https://www.mehr-schulferien.de/api/v2.0/periods"
        self.vacation_type_url = "https://www.mehr-schulferien.de/api/v2.0/holiday_or_vacation_types"
        self.date_format = "%Y-%m-%d"


class GermanVacationContextRuleHandler(context_rule_handler.AbstractContextRuleHandler):

    def __init__(self):

        super().__init__(p_context_name=CALENDAR_CONTEXT_RULE_HANDLER_NAME)

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._vacation_data = None
        self._vacation_type_map = None
        self._federal_state_map = None

        self._config = GermanVacationContextRuleHandlerConfig()
        self._cache = {}

    def get_configuration_section_handler(self):
        return configuration.SimpleConfigurationSectionHandler(p_config_model=self._config)

    def check_vacation_type_map(self):

        if self._vacation_type_map is None:

            url = self._config.vacation_type_url
            request = requests.get(url)

            if request.status_code != 200:
                fmt = "HTTP code {error_code} while downloading {url}"
                raise Exception(fmt.format(error_code=request.status_code, url=url))

            try:
                result = json.loads(request.content.decode("UTF-8"))
                vacation_types = result['data']
                self._vacation_type_map = { vacation_type['id']: vacation_type['name'] for vacation_type in vacation_types}

            except Exception as e:
                fmt = "error {exception} while decoding data from {url}"
                raise Exception(fmt.format(exception=str(e), url=url))

            fmt = "downloaded index metadata for {count} vacation types"
            self._logger.info(fmt.format(count=len(self._vacation_type_map)))



    def check_locations(self):

        if self._federal_state_map is None:

            url = self._config.locations_url
            request = requests.get(url)

            if request.status_code != 200:
                fmt = "HTTP code {error_code} while downloading {url}"
                raise Exception(fmt.format(error_code=request.status_code, url=url))

            try:
                result = json.loads(request.content.decode("UTF-8"))
                locations = result['data']

                fmt = "downloaded {count} locations of Germany"
                self._logger.info(fmt.format(count=len(locations)))

                self._federal_state_map = {location['name']: location['id'] for location in locations if location['is_federal_state']}

            except Exception as e:
                fmt = "error {exception} while decoding data from {url}"
                raise Exception(fmt.format(exception=str(e), url=url))

            fmt = "downloaded index metadata for {count} federal states of Germany"
            self._logger.info(fmt.format(count=len(self._federal_state_map)))


    def check_vacation_data(self):

        if self._vacation_data is None:
            url = self._config.vacation_data_url
            request = requests.get(url)

            if request.status_code != 200:
                fmt = "HTTP code {error_code} while downloading {url}"
                raise Exception(fmt.format(error_code=request.status_code, url=url))

            selected_vacation_types = [ type_id for (type_id, type_name) in self._vacation_type_map.items() if
                                        type_name in ENTRY_FILTER ]


            count = 0

            try:
                result = json.loads(request.content.decode("UTF-8"))
                vacation_entries = result['data']

                self._vacation_data = {}

                for (state_name, state_id) in self._federal_state_map.items():
                    entries = [VacationEntry(name=self._vacation_type_map[entry['holiday_or_vacation_type_id']],
                                             start_date=datetime.datetime.strptime(entry['starts_on'],
                                                                                   self._config.date_format).date(),
                                             end_date=datetime.datetime.strptime(entry['ends_on'],
                                                                                 self._config.date_format).date())
                               for entry in vacation_entries if
                               entry['location_id'] == state_id and
                               entry['holiday_or_vacation_type_id'] in selected_vacation_types]
                    self._vacation_data[state_name] = entries
                    count = count + len(entries)

            except Exception as e:
                fmt = "error {exception} while decoding data from {url}"
                raise Exception(fmt.format(exception=str(e), url=url))

            fmt = "downloaded {count} vacation entries for Germany"
            self._logger.info(fmt.format(count=count))


    def check_data(self):

        self.check_vacation_type_map()
        self.check_locations()
        self.check_vacation_data()


    def is_active(self, p_reference_date, p_details):

        state_name = p_details

        key = "{date}|{state}".format(date=datetime.datetime.strftime(p_reference_date, "%d%m%Y"), state=state_name)

        cached_result = self._cache.get(key)

        if cached_result is not None:
            return cached_result

        self.check_data()

        vacation_entries = self._vacation_data.get(p_details)

        if vacation_entries is None:
            fmt = "unknown federal state name {name}"
            raise configuration.ConfigurationException(fmt.format(name=state_name))

        for entry in vacation_entries:
            if entry.start_date <= p_reference_date <= entry.end_date:
                self._cache[key] = True
                return True

        self._cache[key] = False
        return False
