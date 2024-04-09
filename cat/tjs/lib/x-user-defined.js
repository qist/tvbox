import { inRange, encoderError, end_of_stream, finished, isASCIIByte, isASCIICodePoint } from './text_decoder_utils.js'

// 15.5 x-user-defined

// 15.5.1 x-user-defined decoder
/**
 * @implements {Decoder}
 */
export class XUserDefinedDecoder {
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

    // 3. Return a code point whose value is 0xF780 + byte − 0x80.
    return 0xF780 + bite - 0x80
  }
}

// 15.5.2 x-user-defined encoder
/**
 * @implements {Encoder}
 */
export class XUserDefinedEncoder {
  /**
   * @param {Stream} stream Input stream.
   * @param {number} code_point Next code point read from the stream.
   */
  handler(stream, code_point) {
  // 1.If code point is end-of-stream, return finished.
    if (code_point === end_of_stream)
      return finished

    // 2. If code point is an ASCII code point, return a byte whose
    // value is code point.
    if (isASCIICodePoint(code_point))
      return code_point

    // 3. If code point is in the range U+F780 to U+F7FF, inclusive,
    // return a byte whose value is code point − 0xF780 + 0x80.
    if (inRange(code_point, 0xF780, 0xF7FF))
      return code_point - 0xF780 + 0x80

    // 4. Return error with code point.
    return encoderError(code_point)
  }
}