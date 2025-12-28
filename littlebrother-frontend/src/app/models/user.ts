// Copyright (C) 2019-24  Marcus Rickert
//
// See https://github.com/marcus67/little_brother
// This program is free software; you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation; either version 3 of the License, or
// (at your option) any later version.
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
// You should have received a copy of the GNU General Public License along
// with this program; if not, write to the Free Software Foundation, Inc.,
// 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

import { textSeperator, titleCaseWord } from '../common/tools'

export class User {
  id?: number;
  username?: string;
  active?: boolean;
  configured?: boolean;
  locale?: string;
  process_name_pattern?: string;
  prohibited_process_name_pattern?: string;
  first_name?: string;
  last_name?: string;
  access_code?: string;

	constructor(otherObject?: object) {
	  if (otherObject)
	    Object.assign(this, otherObject)
	}

  full_name(): string | undefined {
    if (this.first_name) 
        if (this.last_name) 
            return this.first_name + " " + this.last_name

        else
            return this.first_name

    else
        return titleCaseWord(this.username)
  }

  summary(languages: Record<string, string> | undefined): (string | undefined)[] {

    var texts: (string| undefined)[] = []

    if (this.username?.toUpperCase != this.full_name()?.toUpperCase())
      texts.push("Username", ": ", this.username)

    if (languages && this.locale && this.locale in languages) {
      var lang = languages[this.locale] ?? "Unknown";

      texts.push(textSeperator, "Locale", ": ", lang)
    }

    return texts;
  }
}
