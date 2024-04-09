import { inRange, decoderError, encoderError, floor, isASCIICodePoint, isASCIIByte,
  end_of_stream, finished } from './text_decoder_utils.js'
import index, { indexCodePointFor, indexShiftJISPointerFor } from './text_decoder_indexes.js'


// 13.3 Shift_JIS

// 13.3.1 Shift_JIS decoder
/**
 * @constructor
 * @implements {Decoder}
 * @param {{fatal: boolean}} options
 */
export class ShiftJISDecoder {
  constructor(options) {
    const { fatal } = options
    this.fatal = fatal
    // Shift_JIS's decoder has an associated Shift_JIS lead (initially
    // 0x00).
    this.Shift_JIS_lead = 0x00
  }
  /**
   * @param {Stream} stream The stream of bytes being decoded.
   * @param {number} bite The next byte read from the stream.
   */
  handler(stream, bite) {
  // 1. If byte is end-of-stream and Shift_JIS lead is not 0x00,
  // set Shift_JIS lead to 0x00 and return error.
    if (bite === end_of_stream && this.Shift_JIS_lead !== 0x00) {
      this.Shift_JIS_lead = 0x00
      return decoderError(this.fatal)
    }

    // 2. If byte is end-of-stream and Shift_JIS lead is 0x00,
    // return finished.
    if (bite === end_of_stream && this.Shift_JIS_lead === 0x00)
      return finished

    // 3. If Shift_JIS lead is not 0x00, let lead be Shift_JIS lead,
    // let pointer be null, set Shift_JIS lead to 0x00, and then run
    // these substeps:
    if (this.Shift_JIS_lead !== 0x00) {
      var lead = this.Shift_JIS_lead
      var pointer = null
      this.Shift_JIS_lead = 0x00

      // 1. Let offset be 0x40, if byte is less than 0x7F, and 0x41
      // otherwise.
      var offset = (bite < 0x7F) ? 0x40 : 0x41

      // 2. Let lead offset be 0x81, if lead is less than 0xA0, and
      // 0xC1 otherwise.
      var lead_offset = (lead < 0xA0) ? 0x81 : 0xC1

      // 3. If byte is in the range 0x40 to 0x7E, inclusive, or 0x80
      // to 0xFC, inclusive, set pointer to (lead − lead offset) ×
      // 188 + byte − offset.
      if (inRange(bite, 0x40, 0x7E) || inRange(bite, 0x80, 0xFC))
        pointer = (lead - lead_offset) * 188 + bite - offset

      // 4. If pointer is in the range 8836 to 10715, inclusive,
      // return a code point whose value is 0xE000 − 8836 + pointer.
      if (inRange(pointer, 8836, 10715))
        return 0xE000 - 8836 + pointer

      // 5. Let code point be null, if pointer is null, and the
      // index code point for pointer in index jis0208 otherwise.
      var code_point = (pointer === null) ? null :
        indexCodePointFor(pointer, index('jis0208'))

      // 6. If code point is null and byte is an ASCII byte, prepend
      // byte to stream.
      if (code_point === null && isASCIIByte(bite))
        stream.prepend(bite)

      // 7. If code point is null, return error.
      if (code_point === null)
        return decoderError(this.fatal)

      // 8. Return a code point whose value is code point.
      return code_point
    }

    // 4. If byte is an ASCII byte or 0x80, return a code point
    // whose value is byte.
    if (isASCIIByte(bite) || bite === 0x80)
      return bite

    // 5. If byte is in the range 0xA1 to 0xDF, inclusive, return a
    // code point whose value is 0xFF61 − 0xA1 + byte.
    if (inRange(bite, 0xA1, 0xDF))
      return 0xFF61 - 0xA1 + bite

    // 6. If byte is in the range 0x81 to 0x9F, inclusive, or 0xE0
    // to 0xFC, inclusive, set Shift_JIS lead to byte and return
    // continue.
    if (inRange(bite, 0x81, 0x9F) || inRange(bite, 0xE0, 0xFC)) {
      this.Shift_JIS_lead = bite
      return null
    }

    // 7. Return error.
    return decoderError(this.fatal)
  }
}

// 13.3.2 Shift_JIS encoder
/**
 * @constructor
 * @implements {Encoder}
 * @param {{fatal: boolean}} options
 */
export class ShiftJISEncoder {
  /**
   * @param {Stream} stream Input stream.
   * @param {number} code_point Next code point read from the stream.
   */
  handler(stream, code_point) {
  // 1. If code point is end-of-stream, return finished.
    if (code_point === end_of_stream)
      return finished

    // 2. If code point is an ASCII code point or U+0080, return a
    // byte whose value is code point.
    if (isASCIICodePoint(code_point) || code_point === 0x0080)
      return code_point

    // 3. If code point is U+00A5, return byte 0x5C.
    if (code_point === 0x00A5)
      return 0x5C

    // 4. If code point is U+203E, return byte 0x7E.
    if (code_point === 0x203E)
      return 0x7E

    // 5. If code point is in the range U+FF61 to U+FF9F, inclusive,
    // return a byte whose value is code point − 0xFF61 + 0xA1.
    if (inRange(code_point, 0xFF61, 0xFF9F))
      return code_point - 0xFF61 + 0xA1

    // 6. If code point is U+2212, set it to U+FF0D.
    if (code_point === 0x2212)
      code_point = 0xFF0D

    // 7. Let pointer be the index Shift_JIS pointer for code point.
    var pointer = indexShiftJISPointerFor(code_point)

    // 8. If pointer is null, return error with code point.
    if (pointer === null)
      return encoderError(code_point)

    // 9. Let lead be floor(pointer / 188).
    var lead = floor(pointer / 188)

    // 10. Let lead offset be 0x81, if lead is less than 0x1F, and
    // 0xC1 otherwise.
    var lead_offset = (lead < 0x1F) ? 0x81 : 0xC1

    // 11. Let trail be pointer % 188.
    var trail = pointer % 188

    // 12. Let offset be 0x40, if trail is less than 0x3F, and 0x41
    // otherwise.
    var offset = (trail < 0x3F) ? 0x40 : 0x41

    // 13. Return two bytes whose values are lead + lead offset and
    // trail + offset.
    return [lead + lead_offset, trail + offset]
  }
}