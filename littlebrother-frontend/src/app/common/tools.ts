import {formatDate} from '@angular/common';

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

export const get_date_as_string = (a_date: Date | undefined, include_seconds:boolean=true) : any => {
  if (a_date)
    return formatDate(a_date, "dd.MM.YYYY HH:mm", "en_US")
  else
    return "-";
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
