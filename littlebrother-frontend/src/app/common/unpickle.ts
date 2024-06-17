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

import { MapType } from "@angular/compiler";

export const unpickle = (object:object, handlers:Map<string, Function>) : any => {

    if (object == null) {
        return null;
    }

    let type = typeof object;

    if (type == "string" || type == "number" || type == "boolean") {
        return object;

    } else if (Array.isArray(object)) {
        let array = []
        for (var i in object) {
            array.push(unpickle(object[i], handlers))
        }
        return array;

    } else if (object instanceof Map) {
        let map = new Map()
        object.forEach( (key, value) => {
            map.set(key, unpickle(value, handlers))
        })
        return map

    } else {
        let className : string | undefined = undefined;
        let newObject = {};

        Object.entries(object).forEach(
            ([key, value]) => {
                if (key == "py/object") {
                    className = value;
                } else {
                    Object.defineProperty(newObject, key, {
                        value: unpickle(value, handlers),
                        enumerable: true
                    });
                }
                //console.log(key + "=" + value)
            }
        );

        if (className) {
            let handler = handlers.get(className);

            if (handler) {
                return handler(newObject);
            } else {
                console.warn("No clue how to unpickle '" + className + "'!");
            }
        }
    }
    return null;
}
