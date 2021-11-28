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
import queue
import time

from little_brother import admin_event
from little_brother.persistence.persistent_dependency_injection_mix_in import PersistenceDependencyInjectionMixIn
from little_brother.persistence.session_context import SessionContext
from python_base_app import log_handling
from python_base_app import tools


class EventHandler(PersistenceDependencyInjectionMixIn):

    def __init__(self, p_host_name, p_is_master):

        super().__init__()

        self._host_name = p_host_name
        self._is_master = p_is_master

        self._logger = log_handling.get_logger(self.__class__.__name__)

        self._event_queue = queue.Queue()
        self._outgoing_events = []
        self._could_not_send = False
        self._event_handlers = {}

    def get_outgoing_events(self):

        outgoing_events = self._outgoing_events
        self._outgoing_events = []
        return outgoing_events

    def register_event_handler(self, p_event_type, p_handler):

        if p_event_type in self._event_handlers:
            msg = "event is '{id}' already registered"
            raise RuntimeError(msg.format(id=p_event_type))

        self._event_handlers[p_event_type] = p_handler

    def queue_event(self, p_event, p_to_master=False, p_is_action=False):

        if p_is_action:
            if p_event.hostname == self._host_name:
                self.queue_event_locally(p_event=p_event)

            else:
                self.queue_event_for_send(p_event=p_event)

        else:
            if p_to_master == self._is_master:
                self.queue_event_locally(p_event=p_event)

            else:
                self.queue_event_for_send(p_event=p_event)

    def queue_event_locally(self, p_event):

        fmt = "Queue locally: {event}"
        self._logger.debug(fmt.format(event=p_event))

        self._event_queue.put(p_event)

    def queue_event_for_send(self, p_event):

        if p_event in self._outgoing_events:
            fmt = "Already in outgoing queue: {event}"
            self._logger.info(fmt.format(event=p_event))
            return

        fmt = "Queue for send: {event}"
        self._logger.debug(fmt.format(event=p_event))

        self._outgoing_events.append(p_event)

    def queue_events(self, p_events, p_to_master=False, p_is_action=False):

        for event in p_events:
            self.queue_event(p_event=event, p_to_master=p_to_master, p_is_action=p_is_action)

    def queue_events_locally(self, p_events):

        for event in p_events:
            self.queue_event_locally(p_event=event)

    def queue_outgoing_event(self, p_event):

        self._outgoing_events.append(p_event)

    def queue_outgoing_events(self, p_events):

        self._outgoing_events.extend(p_events)

    def process_event(self, p_event):

        fmt = "Processing {event}"
        self._logger.debug(fmt.format(event=p_event))

        if p_event.event_type not in self._event_handlers:
            raise RuntimeError("Invalid event type '%s' found" % p_event.event_type)

        new_events = self._event_handlers[p_event.event_type](p_event=p_event)

        if self.persistence is not None:
            with SessionContext(p_persistence=self.persistence) as session_context:
                self.admin_event_entity_manager.log_admin_event(p_session_context=session_context,
                                                                p_admin_event=p_event)

        return new_events

    def delay_event(self, p_event):

        msg = "Delaying execution of event {event} for {secs} seconds..."
        self._logger.debug(msg.format(event=str(p_event), secs=p_event.delay))

        time.sleep(p_event.delay)
        new_events = self.process_event(p_event=p_event)
        self.queue_events(p_events=new_events, p_to_master=True, p_is_action=False)

    def process_queue(self):

        while self._event_queue.qsize() > 0:
            try:
                event = self._event_queue.get(block=False)

            except queue.Empty:
                return

            if event.delay > 0:
                tools.start_simple_thread(lambda: self.delay_event(p_event=event))
                new_events = None

            else:
                new_events = self.process_event(p_event=event)

            if new_events is not None:
                self.queue_events(p_events=new_events, p_to_master=True, p_is_action=False)

    def receive_events(self, p_json_data):

        for json_event in p_json_data:
            event = tools.objectify_dict(p_dict=json_event,
                                         p_class=admin_event.AdminEvent,
                                         p_attribute_classes={
                                             "process_start_time": datetime.datetime,
                                             "event_time": datetime.datetime
                                         })
            self.queue_event_locally(p_event=event)

    def get_return_events(self, p_hostname):

        events = [e for e in self._outgoing_events if e.hostname == p_hostname]

        with SessionContext(p_persistence=self.persistence) as session_context:
            for event in events:
                self.admin_event_entity_manager.log_admin_event(
                    p_session_context=session_context, p_admin_event=event)
                self._outgoing_events.remove(event)

        return events
