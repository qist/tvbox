import * as spider from '%s'

if (!globalThis.__JS_SPIDER__) {
    if (spider.__jsEvalReturn) {
//        globalThis.req = http
        globalThis.__JS_SPIDER__ = spider.__jsEvalReturn()
    } else if (spider.default) {
        globalThis.__JS_SPIDER__ = typeof spider.default === 'function' ? spider.default() : spider.default
    }
}