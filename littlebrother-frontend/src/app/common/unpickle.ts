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