import Stream, { DEFAULT_ENCODING, getEncoding } from './text_decoder_index.js'
import { end_of_stream, finished, codePointsToString } from './text_decoder_utils.js'
import { decoders } from './table.js'

// 8.1 Interface TextDecoder

class TextDecoder {
  /**
   * @param {string=} label The label of the encoding; defaults to 'utf-8'.
   * @param {Object=} options
   */
  constructor(label = DEFAULT_ENCODING, options = {}) {
    // A TextDecoder object has an associated encoding, decoder,
    // stream, ignore BOM flag (initially unset), BOM seen flag
    // (initially unset), error mode (initially replacement), and do
    // not flush flag (initially unset).

    /** @private */
    this._encoding = null
    /** @private @type {?Decoder} */
    this._decoder = null
    /** @private @type {boolean} */
    this._ignoreBOM = false
    /** @private @type {boolean} */
    this._BOMseen = false
    /** @private @type {string} */
    this._error_mode = 'replacement'
    /** @private @type {boolean} */
    this._do_not_flush = false


    // 1. Let encoding be the result of getting an encoding from
    // label.
    const encoding = getEncoding(label)

    // 2. If encoding is failure or replacement, throw a RangeError.
    if (encoding === null || encoding.name == 'replacement')
      throw RangeError('Unknown encoding: ' + label)
    if (!decoders[encoding.name]) {
      throw Error('Decoder not present.' +
                  ' Did you forget to include encoding-indexes.js first?')
    }

    // 4. Set dec's encoding to encoding.
    this._encoding = encoding

    // 5. If options's fatal member is true, set dec's error mode to
    // fatal.
    if (options['fatal'])
      this._error_mode = 'fatal'

    // 6. If options's ignoreBOM member is true, set dec's ignore BOM
    // flag.
    if (options['ignoreBOM'])
      this._ignoreBOM = true
  }

  get encoding() {
    return this._encoding.name.toLowerCase()
  }
  get fatal() {
    return this._error_mode === 'fatal'
  }
  get ignoreBOM() {
    return this._ignoreBOM
  }
  /**
   * @param {BufferSource=} input The buffer of bytes to decode.
   * @param {Object=} options
   * @return The decoded string.
   */
  decode(input, options = {}) {
    let bytes
    if (typeof input === 'object' && input instanceof ArrayBuffer) {
      bytes = new Uint8Array(input)
    } else if (typeof input === 'object' && 'buffer' in input &&
                input.buffer instanceof ArrayBuffer) {
      bytes = new Uint8Array(input.buffer,
        input.byteOffset,
        input.byteLength)
    } else {
      bytes = new Uint8Array(0)
    }

    // 1. If the do not flush flag is unset, set decoder to a new
    // encoding's decoder, set stream to a new stream, and unset the
    // BOM seen flag.
    if (!this._do_not_flush) {
      this._decoder = decoders[this._encoding.name]({
        fatal: this._error_mode === 'fatal' })
      this._BOMseen = false
    }

    // 2. If options's stream is true, set the do not flush flag, and
    // unset the do not flush flag otherwise.
    this._do_not_flush = Boolean(options['stream'])

    // 3. If input is given, push a copy of input to stream.
    // TODO: Align with spec algorithm - maintain stream on instance.
    const input_stream = new Stream(bytes)

    // 4. Let output be a new stream.
    const output = []

    /** @type {?(number|!Array.<number>)} */
    let result

    // 5. While true:
    while (true) {
      // 1. Let token be the result of reading from stream.
      const token = input_stream.read()

      // 2. If token is end-of-stream and the do not flush flag is
      // set, return output, serialized.
      // TODO: Align with spec algorithm.
      if (token === end_of_stream)
        break

      // 3. Otherwise, run these subsubsteps:

      // 1. Let result be the result of processing token for decoder,
      // stream, output, and error mode.
      result = this._decoder.handler(input_stream, token)

      // 2. If result is finished, return output, serialized.
      if (result === finished)
        break

      if (result !== null) {
        if (Array.isArray(result))
          output.push.apply(output, /**@type {!Array.<number>}*/(result))
        else
          output.push(result)
      }

      // 3. Otherwise, if result is error, throw a TypeError.
      // (Thrown in handler)

      // 4. Otherwise, do nothing.
    }
    // TODO: Align with spec algorithm.
    if (!this._do_not_flush) {
      do {
        result = this._decoder.handler(input_stream, input_stream.read())
        if (result === finished)
          break
        if (result === null)
          continue
        if (Array.isArray(result))
          output.push.apply(output, /**@type {!Array.<number>}*/(result))
        else
          output.push(result)
      } while (!input_stream.endOfStream())
      this._decoder = null
    }

    return this.serializeStream(output)
  }
  // A TextDecoder object also has an associated serialize stream
  // algorithm...
  /**
   * @param {!Array.<number>} stream
   */
  serializeStream(stream) {
    // 1. Let token be the result of reading from stream.
    // (Done in-place on array, rather than as a stream)

    // 2. If encoding is UTF-8, UTF-16BE, or UTF-16LE, and ignore
    // BOM flag and BOM seen flag are unset, run these subsubsteps:
    if (['UTF-8', 'UTF-16LE', 'UTF-16BE'].includes(this._encoding.name) &&
        !this._ignoreBOM && !this._BOMseen) {
      if (stream.length > 0 && stream[0] === 0xFEFF) {
        // 1. If token is U+FEFF, set BOM seen flag.
        this._BOMseen = true
        stream.shift()
      } else if (stream.length > 0) {
        // 2. Otherwise, if token is not end-of-stream, set BOM seen
        // flag and append token to stream.
        this._BOMseen = true
      } else {
        // 3. Otherwise, if token is not end-of-stream, append token
        // to output.
        // (no-op)
      }
    }
    // 4. Otherwise, return output.
    return codePointsToString(stream)
  }
}
export {TextDecoder}