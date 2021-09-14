# -*- coding: utf-8 -*-

#    Copyright (C) 2019-2021  Marcus Rickert
#
#    See https://github.com/marcus67/little_brother
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

import unittest

from little_brother import constants
from little_brother import dependency_injection
from little_brother.persistence.persistent_device import Device
from little_brother.persistence.persistent_device_entity_manager import DeviceEntityManager
from little_brother.persistence.session_context import SessionContext
from little_brother.test.web.base_test_status_server import BaseTestStatusServer
from python_base_app.test import base_test

NEW_DEVICE_NAME = "Some Device"
NEW_DEVICE_HOST_NAME = "127.0.0.1"
NEW_DEVICE_MIN_ACTIVITY_DURATION = 321
NEW_DEVICE_MAX_ACTIVE_PING_DELAY = 21
NEW_DEVICE_SAMPLE_SIZE = 32

NEW_INVALID_HOST_NAME = "xxx"
NEW_INVALID_MIN_ACTIVITY_DURATION = constants.DEVICE_MAX_MIN_ACTIVITY_DURATION + 1
NEW_INVALID_SAMPLE_SIZE = constants.DEVICE_MIN_SAMPLE_SIZE - 1
NEW_INVALID_MAX_PING_DELAY = constants.DEVICE_MAX_MAX_ACTIVE_PING_DELAY + 1


class TestStatusServerDevices(BaseTestStatusServer):

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_devices(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        self.login_devices()

        # The second time we call the device page.
        self._driver.get(self._status_server.get_url(p_internal=False, p_rel_url=constants.DEVICES_REL_URL))
        assert constants.APPLICATION_NAME in self._driver.title
        assert "Device Configuration" in self._driver.title

        # we are on the users page right away...
        self.check_empty_device_list()

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_devices_add_and_delete_device(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        self.login_devices()

        device_entity_manager: DeviceEntityManager = dependency_injection.container[DeviceEntityManager]

        with SessionContext(self._persistence) as session_context:
            new_device_name = device_entity_manager.get_new_device_name(
                p_session_context=session_context, p_name_pattern=constants.DEFAULT_DEVICE_NEW_NAME_PATTERN)

            add_button = self._driver.find_element_by_id("add_device")
            add_button.click()

            device: Device = device_entity_manager.get_by_device_name(
                p_session_context=session_context, p_device_name=new_device_name)
            self.assertEqual(new_device_name, device.device_name)

        device_id = device.id

        xpath = "//DIV/A[@aria-controls='detailsdevice_1']"
        self._driver.find_element_by_xpath(xpath)

        delete_button = self._driver.find_element_by_id("delete_device_1")
        delete_button.click()

        delete_button = self._driver.find_element_by_id("delete_device_1-modal-confirm")

        self.click(delete_button)

        with SessionContext(self._persistence) as session_context:
            device = device_entity_manager.get_by_id(
                p_session_context=session_context, p_id=device_id)
            self.assertIsNone(device)

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_devices_edit_device(self):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        device_entity_manager: DeviceEntityManager = dependency_injection.container[DeviceEntityManager]

        with SessionContext(self._persistence) as session_context:
            device_id = device_entity_manager.add_new_device(
                p_session_context=session_context, p_name_pattern=constants.DEFAULT_DEVICE_NEW_NAME_PATTERN)

        self.login_devices()

        elem_prefix = "device_{id}_".format(id=device_id)

        elem = self._driver.find_element_by_id(elem_prefix + "device_name")
        self.set_value(p_elem=elem, p_value=NEW_DEVICE_NAME)

        elem = self._driver.find_element_by_id(elem_prefix + "hostname")
        self.set_value(p_elem=elem, p_value=NEW_DEVICE_HOST_NAME)

        elem = self._driver.find_element_by_id(elem_prefix + "min_activity_duration")
        self.set_value(p_elem=elem, p_value=NEW_DEVICE_MIN_ACTIVITY_DURATION)

        elem = self._driver.find_element_by_id(elem_prefix + "max_active_ping_delay")
        self.set_value(p_elem=elem, p_value=NEW_DEVICE_MAX_ACTIVE_PING_DELAY)

        elem = self._driver.find_element_by_id(elem_prefix + "sample_size")
        self.set_value(p_elem=elem, p_value=NEW_DEVICE_SAMPLE_SIZE)

        save_button = self._driver.find_element_by_id("save")
        self.click(save_button)

        with SessionContext(self._persistence) as session_context:
            device: Device = device_entity_manager.get_by_id(
                p_session_context=session_context, p_id=device_id)
            self.assertIsNotNone(device)
            self.assertEqual(NEW_DEVICE_NAME, device.device_name)
            self.assertEqual(NEW_DEVICE_HOST_NAME, device.hostname)
            self.assertEqual(NEW_DEVICE_MIN_ACTIVITY_DURATION, device.min_activity_duration)
            self.assertEqual(NEW_DEVICE_MAX_ACTIVE_PING_DELAY, device.max_active_ping_delay)
            self.assertEqual(NEW_DEVICE_SAMPLE_SIZE, device.sample_size)

    def _test_page_devices_edit_invalid_data(self, p_elem_name: str, p_invalid_data: str):
        self.create_dummy_status_server()
        self.create_selenium_driver()

        self._status_server.start_server()

        device_entity_manager: DeviceEntityManager = dependency_injection.container[DeviceEntityManager]

        with SessionContext(self._persistence) as session_context:
            device_id = device_entity_manager.add_new_device(
                p_session_context=session_context, p_name_pattern=constants.DEFAULT_DEVICE_NEW_NAME_PATTERN)
            device: Device = device_entity_manager.get_by_id(p_session_context=session_context, p_id=device_id)
            self.assertIsNotNone(device)
            old_value = getattr(device, p_elem_name)

        self.login_devices()

        elem_name_prefix = "device_{id}_".format(id=device_id)

        elem_name = elem_name_prefix + p_elem_name
        elem = self._driver.find_element_by_id(elem_name)
        self.set_value(p_value=p_invalid_data, p_elem=elem)

        save_button = self._driver.find_element_by_id("save")
        self.click(save_button)

        xpath = "//LABEL[@CLASS = 'error-label' and @FOR = '{elem_name}']".format(elem_name=elem_name)
        self._driver.find_element_by_xpath(xpath)

        # Data was not saved!
        with SessionContext(self._persistence) as session_context:
            device: Device = device_entity_manager.get_by_id(p_session_context=session_context, p_id=device_id)
            self.assertIsNotNone(device)
            self.assertEqual(old_value, getattr(device, p_elem_name))

    @base_test.skip_if_env("NO_SELENIUM_TESTS")
    def test_page_devices_edit_invalid_hostname(self):
        self._test_page_devices_edit_invalid_data(
            p_elem_name="hostname", p_invalid_data=NEW_INVALID_HOST_NAME)


if __name__ == "__main__":
    unittest.main()
