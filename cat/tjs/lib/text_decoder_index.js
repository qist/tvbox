import { end_of_stream } from './text_decoder_utils.js'
import { label_to_encoding } from './table.js'

export default class Stream {
  /**
   * A stream represents an ordered sequence of tokens.
   * @param {!(Array.<number>|Uint8Array)} tokens Array of tokens that provide
   * the stream.
   */
  constructor(tokens) {
    this.tokens = [...tokens]
    // Reversed as push/pop is more efficient than shift/unshift.
    this.tokens.reverse()
  }
  /**
   * @returns True if end-of-stream has been hit.
   */
  endOfStream() {
    return !this.tokens.length
  }
  /**
   * When a token is read from a stream, the first token in the
   * stream must be returned and subsequently removed, and
   * end-of-stream must be returned otherwise.
   *
   * @return Get the next token from the stream, or end_of_stream.
   */
  read() {
    if (!this.tokens.length)
      return end_of_stream
    return this.tokens.pop()
  }
  /**
   * When one or more tokens are prepended to a stream, those tokens
   * must be inserted, in given order, before the first token in the
   * stream.
   *
   * @param {(number|!Array.<number>)} token The token(s) to prepend to the
   * stream.
   */
  prepend(token) {
    if (Array.isArray(token)) {
      var tokens = /**@type {!Array.<number>}*/(token)
      while (tokens.length)
        this.tokens.push(tokens.pop())
    } else {
      this.tokens.push(token)
    }
  }
  /**
   * When one or more tokens are pushed to a stream, those tokens
   * must be inserted, in given order, after the last token in the
   * stream.
   *
   * @param {(number|!Array.<number>)} token The tokens(s) to push to the
   * stream.
   */
  push(token) {
    if (Array.isArray(token)) {
      const tokens = /**@type {!Array.<number>}*/(token)
      while (tokens.length)
        this.tokens.unshift(tokens.shift())
    } else {
      this.tokens.unshift(token)
    }
  }
}

export const DEFAULT_ENCODING = 'utf-8'


/**
 * Returns the encoding for the label.
 * @param {string} label The encoding label.
 */
export function getEncoding(label) {
  // 1. Remove any leading and trailing ASCII whitespace from label.
  label = String(label).trim().toLowerCase()

  // 2. If label is an ASCII case-insensitive match for any of the
  // labels listed in the table below, return the corresponding
  // encoding, and failure otherwise.
  if (Object.prototype.hasOwnProperty.call(label_to_encoding, label)) {
    return label_to_encoding[label]
  }
  return null
}


//
// 5. Encodings
//

// 5.1 Encoders and decoders

// /** @interface */
// function Decoder() {}
// Decoder.prototype = {
//   /**
//    * @param {Stream} stream The stream of bytes being decoded.
//    * @param {number} bite The next byte read from the stream.
//    * @return {?(number|!Array.<number>)} The next code point(s)
//    *     decoded, or null if not enough data exists in the input
//    *     stream to decode a complete code point, or |finished|.
//    */
//   handler: function(stream, bite) {},
// }

// /** @interface */
// function Encoder() {}
// Encoder.prototype = {
//   /**
//    * @param {Stream} stream The stream of code points being encoded.
//    * @param {number} code_point Next code point read from the stream.
//    * @return {(number|!Array.<number>)} Byte(s) to emit, or |finished|.
//    */
//   handler: function(stream, code_point) {},
// }