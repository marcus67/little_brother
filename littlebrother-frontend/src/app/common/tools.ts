import {formatDate} from '@angular/common';

const durationRe = /((?<hours>[0-9]+)h)?((?<minutes>[0-9]+)m)?((?<seconds>[0-9]+)s)?/g;
export const timeValidationPattern = "^-$|^[012]?[0-9]:[0-5][0-9]$"
export const timeDurationPattern = "^-$|^([0-9]+h)?([0-9]+m)?$"

export const get_duration_as_string = (seconds: number | undefined, include_seconds:boolean=false) : any => {
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
        return "-"
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
//    return new Date(Date.UTC(+b[0], +b[1], +b[2], +b[3], +b[4], +b[5]));
    return new Date(a_string);
  } else {
    return undefined;
  }
}

function zeroPad(num:number, numZeros: number) {
    var n = Math.abs(num);
    var zeros = Math.max(0, numZeros - Math.floor(n).toString().length );
    var zeroString = Math.pow(10,zeros).toString().substr(1);
    if( num < 0 ) {
        zeroString = '-' + zeroString;
    }

    return zeroString+n;
}
