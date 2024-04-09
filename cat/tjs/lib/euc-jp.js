import { inRange, decoderError, encoderError, isASCIICodePoint,
  end_of_stream, finished, isASCIIByte, floor } from './text_decoder_utils.js'
import index, { indexCodePointFor, indexPointerFor } from './text_decoder_indexes.js'

//
// 13. Legacy multi-byte Japanese encodings
//

// 13.1 euc-jp

// 13.1.1 euc-jp decoder
/**
 * @implements {Decoder}
 */
export class EUCJPDecoder {
  constructor(options) {
    const { fatal } = options
    this.fatal = fatal

    // euc-jp's decoder has an associated euc-jp jis0212 flag
    // (initially unset) and euc-jp lead (initially 0x00).
    this.eucjp_jis0212_flag = false
    this.eucjp_lead = 0x00
  }

  /**
   * @param {Stream} stream The stream of bytes being decoded.
   * @param {number} bite The next byte read from the stream.
   */
  handler(stream, bite) {
  // 1. If byte is end-of-stream and euc-jp lead is not 0x00, set
  // euc-jp lead to 0x00, and return error.
    if (bite === end_of_stream && this.eucjp_lead !== 0x00) {
      this.eucjp_lead = 0x00
      return decoderError(this.fatal)
    }

    // 2. If byte is end-of-stream and euc-jp lead is 0x00, return
    // finished.
    if (bite === end_of_stream && this.eucjp_lead === 0x00)
      return finished

    // 3. If euc-jp lead is 0x8E and byte is in the range 0xA1 to
    // 0xDF, inclusive, set euc-jp lead to 0x00 and return a code
    // point whose value is 0xFF61 − 0xA1 + byte.
    if (this.eucjp_lead === 0x8E && inRange(bite, 0xA1, 0xDF)) {
      this.eucjp_lead = 0x00
      return 0xFF61 - 0xA1 + bite
    }

    // 4. If euc-jp lead is 0x8F and byte is in the range 0xA1 to
    // 0xFE, inclusive, set the euc-jp jis0212 flag, set euc-jp lead
    // to byte, and return continue.
    if (this.eucjp_lead === 0x8F && inRange(bite, 0xA1, 0xFE)) {
      this.eucjp_jis0212_flag = true
      this.eucjp_lead = bite
      return null
    }

    // 5. If euc-jp lead is not 0x00, let lead be euc-jp lead, set
    // euc-jp lead to 0x00, and run these substeps:
    if (this.eucjp_lead !== 0x00) {
      const lead = this.eucjp_lead
      this.eucjp_lead = 0x00

      // 1. Let code point be null.
      let code_point = null

      // 2. If lead and byte are both in the range 0xA1 to 0xFE,
      // inclusive, set code point to the index code point for (lead
      // − 0xA1) × 94 + byte − 0xA1 in index jis0208 if the euc-jp
      // jis0212 flag is unset and in index jis0212 otherwise.
      if (inRange(lead, 0xA1, 0xFE) && inRange(bite, 0xA1, 0xFE)) {
        code_point = indexCodePointFor(
          (lead - 0xA1) * 94 + (bite - 0xA1),
          index(!this.eucjp_jis0212_flag ? 'jis0208' : 'jis0212'))
      }

      // 3. Unset the euc-jp jis0212 flag.
      this.eucjp_jis0212_flag = false

      // 4. If byte is not in the range 0xA1 to 0xFE, inclusive,
      // prepend byte to stream.
      if (!inRange(bite, 0xA1, 0xFE))
        stream.prepend(bite)

      // 5. If code point is null, return error.
      if (code_point === null)
        return decoderError(this.fatal)

      // 6. Return a code point whose value is code point.
      return code_point
    }

    // 6. If byte is an ASCII byte, return a code point whose value
    // is byte.
    if (isASCIIByte(bite))
      return bite

    // 7. If byte is 0x8E, 0x8F, or in the range 0xA1 to 0xFE,
    // inclusive, set euc-jp lead to byte and return continue.
    if (bite === 0x8E || bite === 0x8F || inRange(bite, 0xA1, 0xFE)) {
      this.eucjp_lead = bite
      return null
    }

    // 8. Return error.
    return decoderError(this.fatal)
  }
}

// 13.1.2 euc-jp encoder
/**
 * @implements {Encoder}
 */
export class EUCJPEncoder {
  /**
   * @param {Stream} stream Input stream.
   * @param {number} code_point Next code point read from the stream.
   */
  handler(stream, code_point) {
  // 1. If code point is end-of-stream, return finished.
    if (code_point === end_of_stream)
      return finished

    // 2. If code point is an ASCII code point, return a byte whose
    // value is code point.
    if (isASCIICodePoint(code_point))
      return code_point

    // 3. If code point is U+00A5, return byte 0x5C.
    if (code_point === 0x00A5)
      return 0x5C

    // 4. If code point is U+203E, return byte 0x7E.
    if (code_point === 0x203E)
      return 0x7E

    // 5. If code point is in the range U+FF61 to U+FF9F, inclusive,
    // return two bytes whose values are 0x8E and code point −
    // 0xFF61 + 0xA1.
    if (inRange(code_point, 0xFF61, 0xFF9F))
      return [0x8E, code_point - 0xFF61 + 0xA1]

    // 6. If code point is U+2212, set it to U+FF0D.
    if (code_point === 0x2212)
      code_point = 0xFF0D

    // 7. Let pointer be the index pointer for code point in index
    // jis0208.
    const pointer = indexPointerFor(code_point, index('jis0208'))

    // 8. If pointer is null, return error with code point.
    if (pointer === null)
      return encoderError(code_point)

    // 9. Let lead be floor(pointer / 94) + 0xA1.
    const lead = floor(pointer / 94) + 0xA1

    // 10. Let trail be pointer % 94 + 0xA1.
    const trail = pointer % 94 + 0xA1

    // 11. Return two bytes whose values are lead and trail.
    return [lead, trail]
  }
}