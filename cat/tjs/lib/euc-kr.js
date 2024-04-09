import { inRange, decoderError, encoderError, isASCIICodePoint,
  end_of_stream, finished, isASCIIByte, floor } from './text_decoder_utils.js'
import index, { indexCodePointFor, indexPointerFor } from './text_decoder_indexes.js'

//
// 14. Legacy multi-byte Korean encodings
//

// 14.1 euc-kr

// 14.1.1 euc-kr decoder
/**
 * @implements {Decoder}
 */
export class EUCKRDecoder {
  constructor(options) {
    const { fatal } = options
    this.fatal = fatal
    // euc-kr's decoder has an associated euc-kr lead (initially 0x00).
    this.euckr_lead = 0x00
  }
  /**
   * @param {Stream} stream The stream of bytes being decoded.
   * @param {number} bite The next byte read from the stream.
   */
  handler(stream, bite) {
    // 1. If byte is end-of-stream and euc-kr lead is not 0x00, set
    // euc-kr lead to 0x00 and return error.
    if (bite === end_of_stream && this.euckr_lead !== 0) {
      this.euckr_lead = 0x00
      return decoderError(this.fatal)
    }

    // 2. If byte is end-of-stream and euc-kr lead is 0x00, return
    // finished.
    if (bite === end_of_stream && this.euckr_lead === 0)
      return finished

    // 3. If euc-kr lead is not 0x00, let lead be euc-kr lead, let
    // pointer be null, set euc-kr lead to 0x00, and then run these
    // substeps:
    if (this.euckr_lead !== 0x00) {
      const lead = this.euckr_lead
      let pointer = null
      this.euckr_lead = 0x00

      // 1. If byte is in the range 0x41 to 0xFE, inclusive, set
      // pointer to (lead − 0x81) × 190 + (byte − 0x41).
      if (inRange(bite, 0x41, 0xFE))
        pointer = (lead - 0x81) * 190 + (bite - 0x41)

      // 2. Let code point be null, if pointer is null, and the
      // index code point for pointer in index euc-kr otherwise.
      const code_point = (pointer === null)
        ? null : indexCodePointFor(pointer, index('euc-kr'))

      // 3. If code point is null and byte is an ASCII byte, prepend
      // byte to stream.
      if (pointer === null && isASCIIByte(bite))
        stream.prepend(bite)

      // 4. If code point is null, return error.
      if (code_point === null)
        return decoderError(this.fatal)

      // 5. Return a code point whose value is code point.
      return code_point
    }

    // 4. If byte is an ASCII byte, return a code point whose value
    // is byte.
    if (isASCIIByte(bite))
      return bite

    // 5. If byte is in the range 0x81 to 0xFE, inclusive, set
    // euc-kr lead to byte and return continue.
    if (inRange(bite, 0x81, 0xFE)) {
      this.euckr_lead = bite
      return null
    }

    // 6. Return error.
    return decoderError(this.fatal)
  }
}

// 14.1.2 euc-kr encoder
/**
 * @implements {Encoder}
 */
export class EUCKREncoder {
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
    // euc-kr.
    const pointer = indexPointerFor(code_point, index('euc-kr'))

    // 4. If pointer is null, return error with code point.
    if (pointer === null)
      return encoderError(code_point)

    // 5. Let lead be floor(pointer / 190) + 0x81.
    const lead = floor(pointer / 190) + 0x81

    // 6. Let trail be pointer % 190 + 0x41.
    const trail = (pointer % 190) + 0x41

    // 7. Return two bytes whose values are lead and trail.
    return [lead, trail]
  }
}