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
import re
from xml.etree import ElementTree

import requests

from little_brother import constants
from little_brother import settings
from python_base_app import log_handling, tools
from python_base_app.configuration import ConfigModel

SECTION_NAME = "VersionChecker"
DEFAULT_CHECK_INTERVAL_IN_DAYS = 1


class VersionInfo:

    def __init__(self, p_version: str = None, p_revision: int = None):
        self.version = p_version
        self.revision = int(p_revision)


class ChannelInfo:

    def __init__(self, p_channel: str, p_download_url: str):
        self.channel = p_channel
        self.download_url = p_download_url


SOURCEFORGE_CHANNEL_INFOS = {
    settings.MASTER_BRANCH_NAME: ChannelInfo(p_channel=settings.MASTER_BRANCH_NAME,
                                             p_download_url="https://sourceforge.net/projects/little-brother/files/"
                                                            "master/little-brother_{version}_{revision}.deb/download"),
    settings.RELEASE_BRANCH_NAME: ChannelInfo(p_channel=settings.MASTER_BRANCH_NAME,
                                              p_download_url="https://sourceforge.net/projects/little-brother/files/"
                                                             "release/little-brother_{version}_{revision}.deb/download")
}


class VersionCheckerConfigModel(ConfigModel):

    def is_active(self):
        return True

    def __init__(self):
        super().__init__(p_section_name=SECTION_NAME)

        self.sourceforge_version_rss_url = constants.SOURCEFORGE_VERSION_RSS_URL
        self.sourceforge_version_xpath = constants.SOURCEFORGE_VERSION_XPATH
        self.sourceforge_version_regex = constants.SOURCEFORGE_VERSION_REGEX
        self.check_interval_in_days = DEFAULT_CHECK_INTERVAL_IN_DAYS


class VersionChecker:

    def __init__(self, p_config: VersionCheckerConfigModel, p_channel_infos):

        self._config = p_config
        self._channel_infos = p_channel_infos
        self._next_check = None
        self._version_infos = None

        self._logger = log_handling.get_logger(SECTION_NAME)

    def retrieve_version_infos(self):

        if self._config.check_interval_in_days == 0:
            return

        current_time = tools.get_current_time()

        if self._version_infos is not None and \
                self._next_check is not None and \
                current_time < self._next_check:
            return

        self._next_check = current_time + datetime.timedelta(days=self._config.check_interval_in_days)

        try:

            fmt = "Retrieving version information from RSS feed {rss}..."
            self._logger.info(fmt.format(rss=self._config.sourceforge_version_rss_url))

            req = requests.get(self._config.sourceforge_version_rss_url)

            tree = ElementTree.ElementTree(ElementTree.fromstring(req.content))

            fmt = "{xpath}"
            xpath = fmt.format(xpath=self._config.sourceforge_version_xpath)
            items = tree.findall(xpath)

            regex = re.compile(self._config.sourceforge_version_regex)

            self._version_infos = {channel: None for channel in self._channel_infos.keys()}

            # self._version_infos['master'] = VersionInfo(p_version='0.4.9', p_revision=109)

            for item in items:
                match = regex.match(item.text)

                if match:
                    channel = match.group(1)

                    if channel not in self._version_infos:
                        fmt = "invalid channel '{channel}' in RSS item '{item}'"
                        self._logger.warning(fmt.format(channel=channel, item=item.text))
                        continue

                    revision = int(match.group(3))
                    old_version_info: VersionInfo = self._version_infos.get(channel)

                    if old_version_info is None or int(revision) > old_version_info.revision:
                        self._version_infos[channel] = VersionInfo(p_version=match.group(2), p_revision=revision)

            for channel in self._channel_infos.keys():
                version_info: VersionInfo = self._version_infos.get(channel)

                if version_info is not None:
                    fmt = "Channel '{channel}' has latest version {version} with revision {revision}"
                    self._logger.debug(
                        fmt.format(channel=channel, version=version_info.version, revision=version_info.revision))

        except Exception as e:

            fmt = "Exception '{msg}' while retrieving RSS feed at {url}"
            self._logger.error(fmt.format(msg=str(e), url=self._config.sourceforge_version_rss_url))

    @property
    def version_infos(self):

        self.retrieve_version_infos()
        return self._version_infos

    def get_download_url(self, p_channel) -> ChannelInfo:

        self.retrieve_version_infos()

        if self._version_infos is None:
            return None

        version_info = self._version_infos.get(p_channel)
        url_format = self._channel_infos.get(p_channel).download_url

        return url_format.format(version=version_info.version, revision=version_info.revision, channel=p_channel)

    def is_revision_current(self, p_channel: str, p_revision: int):

        self.retrieve_version_infos()

        if self._version_infos is None:
            return None

        version_info = self._version_infos.get(p_channel)

        if version_info is None:
            return None

        if version_info.revision <= int(p_revision):
            return None

        return version_info
