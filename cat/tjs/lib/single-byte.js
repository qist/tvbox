import { end_of_stream, finished, isASCIIByte, decoderError, encoderError, isASCIICodePoint } from './text_decoder_utils.js'
import { indexPointerFor } from './text_decoder_indexes.js'

//
// 10. Legacy single-byte encodings
//

// 10.1 single-byte decoder
/**
 * @implements {Decoder}
 */
export class SingleByteDecoder {
  /**
   * @param {!Array.<number>} index The encoding index.
   * @param {{fatal: boolean}} options
   */
  constructor(index, options) {
    const { fatal } = options
    this.fatal = fatal
    this.index = index
  }
  /**
   * @param {Stream} stream The stream of bytes being decoded.
   * @param {number} bite The next byte read from the stream.
   */
  handler(stream, bite) {
  // 1. If byte is end-of-stream, return finished.
    if (bite === end_of_stream)
      return finished

    // 2. If byte is an ASCII byte, return a code point whose value
    // is byte.
    if (isASCIIByte(bite))
      return bite

    // 3. Let code point be the index code point for byte − 0x80 in
    // index single-byte.
    var code_point = this.index[bite - 0x80]

    // 4. If code point is null, return error.
    if (code_point === null)
      return decoderError(this.fatal)

    // 5. Return a code point whose value is code point.
    return code_point
  }
}

// 10.2 single-byte encoder
/**
 * @implements {Encoder}
 */
export class SingleByteEncoder {
  /**
   * @param {!Array.<?number>} index The encoding index.
   */
  constructor(index) {
    this.index = index
  }
  /**
   * @param {Stream} stream Input stream.
   * @param {number} code_point Next code point read from the stream.
   * @return {(number|!Array.<number>)} Byte(s) to emit.
   */
  handler(stream, code_point) {
    // 1. If code point is end-of-stream, return finished.
    if (code_point === end_of_stream)
      return finished

    // 2. If code point is an ASCII code point, return a byte whose
    // value is code point.
    if (isASCIICodePoint(code_point))
      return code_point

    // 3. Let pointer be the index pointer for code point in index
    // single-byte.
    const pointer = indexPointerFor(code_point, this.index)

    // 4. If pointer is null, return error with code point.
    if (pointer === null)
      encoderError(code_point)

    // 5. Return a byte whose value is pointer + 0x80.
    return pointer + 0x80
  }
}