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

from python_base_app import log_handling
from python_base_app import configuration
from python_base_app import base_app

from little_brother import admin_event#

class ProcessHandlerConfigModel(configuration.ConfigModel):
    
    def __init__(self, p_section_name):
        super(ProcessHandlerConfigModel, self).__init__(p_section_name=p_section_name)

        self.check_interval = base_app.DEFAULT_TASK_INTERVAL
                    

class ProcessHandler(object):


    def __init__(self, p_config):
        
        self._config = p_config
        
        self._logger = log_handling.get_logger(self.__class__.__name__)
        
        self._process_infos = {}
                
    @property    
    def process_infos(self):
        
        return self._process_infos
    
    @property
    def id(self):        
        return self.__class__.__name__
    
    def can_kill_processes(self):
        return False
        
    def handle_event_process_start(self, p_event):
        
        key = p_event.get_key()
        updated = False
        
        if key in self._process_infos:
            
            fmt = "process of '%s' already started -> resetting end time" % str(p_event)
            self._logger.warning(fmt)
            
            pinfo = self._process_infos[key]
            pinfo.end_time = None
            updated = True 
        
        else:
            pinfo = admin_event.create_process_info_from_event(p_event=p_event)
            
            fmt = "STARTED %s" % str(pinfo)
            self._logger.debug(fmt)
            
            self._process_infos[key] = pinfo
            
        return (pinfo, updated)
        

    def handle_event_process_end(self, p_event):
        
        key = p_event.get_key()
        
        if key not in self._process_infos:
            fmt = "process of %s does not exist -> ignoring event" % str(p_event)
            self._logger.warning(fmt)
            return None
        
        pinfo = self._process_infos[key]
        pinfo.end_time = p_event.event_time
        
        fmt = "TERMINATED %s" % str(pinfo)
        self._logger.debug(fmt)
        
        return pinfo
        
    def handle_event_kill_process(self, p_event):
        pass        
    
    def add_historic_process(self, p_process_info):
        self._process_infos[p_process_info.get_key()] = p_process_info
    
        
    def get_artificial_termination_events(self):
        events = [ self.create_admin_event_process_end_from_pinfo(p_pinfo=pinfo) for pinfo in self._process_infos.values() if pinfo.is_active() ]
                        
        return events

    def get_artificial_activation_events(self):
        events = [ self.create_admin_event_process_start_from_pinfo(p_pinfo=pinfo) for pinfo in self._process_infos.values() if pinfo.is_active() ]
                        
        return events
        
    
    def create_admin_event_process_end_from_pinfo(self, p_pinfo, p_reference_time = None):
        if p_reference_time is None:
            p_reference_time = datetime.datetime.now()
        
        return admin_event.AdminEvent(
                    p_event_type=admin_event.EVENT_TYPE_PROCESS_END,
                    p_hostname=p_pinfo.hostname,
                    p_username=p_pinfo.username,
                    p_processhandler=p_pinfo.processhandler,
                    p_process_start_time=p_pinfo.start_time,
                    p_event_time=p_reference_time,
                    p_pid=p_pinfo.pid)    

    def create_admin_event_process_start_from_pinfo(self, p_pinfo, p_reference_time = None):
        if p_reference_time is None:
            p_reference_time = datetime.datetime.now()
        
        return admin_event.AdminEvent(
                    p_event_type=admin_event.EVENT_TYPE_PROCESS_START,
                    p_hostname=p_pinfo.hostname,
                    p_username=p_pinfo.username,
                    p_processhandler=p_pinfo.processhandler,
                    p_process_start_time=p_reference_time,
                    p_event_time=datetime.datetime.now(),
                    p_pid=p_pinfo.pid)    
    
    
    def scan_processes(self, p_uid_map, p_host_name, p_process_regex_map):
        pass
    
