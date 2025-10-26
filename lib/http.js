// globalThis.md5 = md5X;
let req = (url, options) => http(url, Object.assign({
    async: false
}, options));
globalThis.req = (url, options) => http(url, Object.assign({
    async: false
}, options));

function http(url, options = {}) {
    if (options?.async === false) return _http(url, options)
    return new Promise(resolve => _http(url, Object.assign({
        complete: res => resolve(res)
    }, options))).catch(err => {
        console.error(err.name, err.message, err.stack)
        return {
            ok: false,
            status: 500,
            url
        }
    })
}

Object.defineProperty(globalThis, 'global', {
    enumerable: true,
    get() {
        return globalThis;
    },
    set() {}
});

Object.defineProperty(globalThis, 'window', {
    enumerable: true,
    get() {
        return globalThis;
    },
    set() {}
});

Object.defineProperty(globalThis, 'self', {
    enumerable: true,
    get() {
        return globalThis;
    },
    set() {}
});
