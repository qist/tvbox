import Stream, { DEFAULT_ENCODING, getEncoding } from './text_decoder_index.js'
import { end_of_stream, finished, stringToCodePoints } from './text_decoder_utils.js'
import { encoders } from './table.js'

// 8.2 Interface TextEncoder

class TextEncoder {
  /**
   * @param {string=} label The label of the encoding. NONSTANDARD.
   * @param {Object=} [options] NONSTANDARD.
   */
  constructor(label, options = {}) {
    // A TextEncoder object has an associated encoding and encoder.

    /** @private */
    this._encoding = null
    /** @private @type {?Encoder} */
    this._encoder = null

    // Non-standard
    /** @private @type {boolean} */
    this._do_not_flush = false
    /** @private @type {string} */
    this._fatal = options['fatal'] ? 'fatal' : 'replacement'

    // 2. Set enc's encoding to UTF-8's encoder.
    if (options['NONSTANDARD_allowLegacyEncoding']) {
      // NONSTANDARD behavior.
      label = label !== undefined ? String(label) : DEFAULT_ENCODING
      var encoding = getEncoding(label)
      if (encoding === null || encoding.name === 'replacement')
        throw RangeError('Unknown encoding: ' + label)
      if (!encoders[encoding.name]) {
        throw Error('Encoder not present.' +
                    ' Did you forget to include encoding-indexes.js first?')
      }
      this._encoding = encoding
    } else {
      // Standard behavior.
      this._encoding = getEncoding('utf-8')

      if (label !== undefined && 'console' in global) {
        console.warn('TextEncoder constructor called with encoding label, '
                      + 'which is ignored.')
      }
    }
  }
  get encoding() {
    return this._encoding.name.toLowerCase()
  }
  /**
   * @param {string=} opt_string The string to encode.
   * @param {Object=} options
   */
  encode(opt_string = '', options = {}) {
    // NOTE: This option is nonstandard. None of the encodings
    // permitted for encoding (i.e. UTF-8, UTF-16) are stateful when
    // the input is a USVString so streaming is not necessary.
    if (!this._do_not_flush)
      this._encoder = encoders[this._encoding.name]({
        fatal: this._fatal === 'fatal' })
    this._do_not_flush = Boolean(options['stream'])

    // 1. Convert input to a stream.
    const input = new Stream(stringToCodePoints(opt_string))

    // 2. Let output be a new stream
    const output = []

    /** @type {?(number|!Array.<number>)} */
    var result
    // 3. While true, run these substeps:
    while (true) {
      // 1. Let token be the result of reading from input.
      var token = input.read()
      if (token === end_of_stream)
        break
      // 2. Let result be the result of processing token for encoder,
      // input, output.
      result = this._encoder.handler(input, token)
      if (result === finished)
        break
      if (Array.isArray(result))
        output.push.apply(output, /**@type {!Array.<number>}*/(result))
      else
        output.push(result)
    }
    // TODO: Align with spec algorithm.
    if (!this._do_not_flush) {
      while (true) {
        result = this._encoder.handler(input, input.read())
        if (result === finished)
          break
        if (Array.isArray(result))
          output.push.apply(output, /**@type {!Array.<number>}*/(result))
        else
          output.push(result)
      }
      this._encoder = null
    }
    // 3. If result is finished, convert output into a byte sequence,
    // and then return a Uint8Array object wrapping an ArrayBuffer
    // containing output.
    return new Uint8Array(output)
  }
}
export {TextEncoder}