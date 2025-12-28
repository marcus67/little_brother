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

import {formatDate} from '@angular/common';
import { constants } from 'buffer';

const durationRe = /((?<hours>[0-9]+)h)?((?<minutes>[0-9]+)m)?((?<seconds>[0-9]+)s)?/g;
export const timeValidationPattern = "^-$|^[012]?[0-9]:[0-5][0-9]$"
export const timeDurationPattern = "^-$|^([0-9]+h)?([0-9]+m)?$"
export const textSeperator = ' <i style="font-size: 0.5rem; vertical-align: +25%" class="fas fa-circle fa-sm"></i> '

export const get_duration_as_string = (seconds: number | undefined, dash_on_missing=true,
                                       include_seconds:boolean=false) : any => {
    if (seconds) {
        let hours = Math.trunc(seconds / 3600)
        let minutes = Math.trunc((seconds - hours * 3600) / 60)

        if (include_seconds) {
            let remaining_seconds = Math.trunc(seconds - hours * 3600 - minutes * 60)
            return hours + "h" + zeroPad(minutes,2) + "m" + zeroPad(remaining_seconds, 2) + "s"
        } else {
            return hours + "h" + zeroPad(minutes,2) + "m"
        }
    } else {
        if (dash_on_missing)
          return "-"
        else
          return undefined
    }
}

export const get_duration_in_seconds_from_string = (a_string: string) : number | undefined => {
  a_string = a_string?.trim()

  if (a_string == "-" || a_string == "")
    return undefined;

  var result = [...a_string.matchAll(durationRe)];

  if (result && result[0] && result[0].groups) {
    var duration : number = 0

    if (result[0].groups["hours"])
      duration += 3600 * +result[0].groups["hours"];

    if (result[0].groups["minutes"])
      duration += 60 * +result[0].groups["minutes"];

    if (result[0].groups["seconds"])
      duration += +result[0].groups["seconds"];

    return duration;
  } else {
    throw new TypeError("duration must have format [NNh][NNm][NNs]")
  }

}

export const get_date_as_string = (a_date: Date | undefined, include_date:boolean=true) : any => {
  if (a_date)
    if (include_date)
      return formatDate(a_date, "dd.MM.YYYY HH:mm", "en_US")
    else
      return formatDate(a_date, "HH:mm", "en_US")
  else
    return "-";
}

export const get_iso_8601_from_time_string = (a_string: string | undefined) : string | undefined => {
  a_string = a_string?.trim()

  if (a_string == "-")
    return undefined;

  if (a_string?.length == 4)
    a_string = "0" + a_string;

  return "1900-01-01T" + a_string + ":00Z";
}

export const get_date_from_iso_string = (a_string: string | undefined) : any => {
  if (a_string) {
    var b = a_string.split(/\D+/);
    return new Date(a_string);
  } else {
    return undefined;
  }
}

function zeroPad(num:number, numZeros: number) {
    var n = Math.abs(num);
    var zeros = Math.max(0, numZeros - Math.floor(n).toString().length );
    var zeroString = Math.pow(10,zeros).toString().substring(1);
    if( num < 0 ) {
        zeroString = '-' + zeroString;
    }

    return zeroString+n;
}


export const titleCaseWord = (word: string | undefined) : string | undefined => {
  if (!word) 
    return word;
  return word[0].toUpperCase() + word.substring(1).toLowerCase();
}


export const format_text_array = (elements: (string | undefined)[]) : string => {

  var text = ""

  for (const element of elements) {
      if (element == textSeperator) {
          if (text != "")
              text += textSeperator
      } else {
        text += element
      }
    }

  return text
}
