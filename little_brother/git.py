# -*- coding: utf-8 -*-

# Copyright (C) 2021  Marcus Rickert
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

git_metadata = {
    "commit_id": "<unknown>",
    "branch": "<unknown>",
    "author_name": "<unknown>",
    "author_email": "<unknown>"
}

try:
    from little_brother import git_metadata

    git_metadata = {
        "commit_id": git_metadata.GIT_COMMIT_ID[0:16],
        "branch": git_metadata.GIT_BRANCH,
        "author_name": git_metadata.GIT_AUTHOR_NAME,
        "author_email":git_metadata.GIT_AUTHOR_EMAIL
    }

except Exception as e:
    print(str(e))